import pandas as pd
from sqlalchemy import create_engine, text
import os
from datetime import datetime
import ast
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

# Load environment variables
load_dotenv()

# Database connection settings
DB_URL = os.getenv('LOCAL_DATABASE_URL', 'postgresql://postgres:Mac.phil.007@localhost:5432/orientor_db')

def clean_hobbies(hobbies_str):
    """Convert string representation of list to comma-separated string."""
    try:
        if pd.isna(hobbies_str):
            return ''
        # Try to evaluate the string as a list
        hobbies_list = ast.literal_eval(hobbies_str)
        # Join the list elements with commas
        return ', '.join(hobbies_list)
    except:
        # If there's any error, return the original string
        return str(hobbies_str) if not pd.isna(hobbies_str) else ''

def upload_data():
    try:
        # Create database connection
        engine = create_engine(DB_URL)
        
        # Read CSV files
        print("Reading CSV files...")
        students_df = pd.read_csv('/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/data/df_students.csv')
        users_df = pd.read_csv('/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/data/df_users.csv')
        
        print(f"Found {len(students_df)} students and {len(users_df)} users in CSV files")
        
        # Process students data
        students_df = students_df.rename(columns={
            'Name': 'name',
            'Age': 'age',
            'Sex': 'sex',
            'Major': 'major',
            'Year': 'year',
            'GPA': 'gpa',
            'Hobbies': 'hobbies',
            'Country': 'country',
            'State/Province': 'state_province',
            'Unique Quality': 'unique_quality',
            'Story': 'story',
            'Favourite movie': 'favorite_movie',
            'Favourite Book': 'favorite_book',
            'Role Model': 'favorite_celebrities',
            'Learning Style': 'learning_style',
            'Interests': 'interests',
            'ID': 'id',
            'user_id': 'user_id'
        })
        
        # Drop the 'id' column as we're using user_id
        students_df = students_df.drop(columns=['id'])
        
        # Clean text fields that might contain lists
        students_df['hobbies'] = students_df['hobbies'].apply(clean_hobbies)
        students_df['interests'] = students_df['interests'].apply(clean_hobbies)
        
        # Add timestamps
        current_time = datetime.now()
        students_df['created_at'] = current_time
        students_df['updated_at'] = current_time
        
        # Ensure numeric fields have correct types
        students_df['age'] = pd.to_numeric(students_df['age'], errors='coerce').astype('Int64')
        students_df['year'] = pd.to_numeric(students_df['year'], errors='coerce').astype('Int64')
        students_df['gpa'] = pd.to_numeric(students_df['gpa'], errors='coerce')
        
        # Ensure string fields don't exceed max lengths
        string_fields = {
            'name': 255,
            'sex': 50,
            'major': 255,
            'country': 255,
            'state_province': 255,
            'favorite_movie': 255,
            'favorite_book': 255,
            'learning_style': 50
        }
        
        for field, max_length in string_fields.items():
            if field in students_df.columns:
                students_df[field] = students_df[field].astype(str).str.slice(0, max_length)
        
        # Process users data
        users_df = users_df.rename(columns={
            'ID': 'id',
            'email': 'email',
            'hashed_password': 'hashed_password',
            'created_at': 'created_at'
        })
        
        # Convert created_at to datetime
        users_df['created_at'] = pd.to_datetime(users_df['created_at'])
        
        successful_users = 0
        failed_users = 0
        failed_emails = []

        # Upload users in smaller batches
        batch_size = 100  # Reduced batch size
        for i in range(0, len(users_df), batch_size):
            batch_df = users_df.iloc[i:i + batch_size]
            try:
                with engine.begin() as conn:
                    batch_df.to_sql('users', conn, if_exists='append', index=False)
                successful_users += len(batch_df)
                print(f"Uploaded users batch {i//batch_size + 1}/{len(users_df)//batch_size + 1}")
            except IntegrityError as e:
                if isinstance(e.orig, UniqueViolation):
                    print(f"Handling duplicates in batch {i//batch_size + 1}")
                    for _, row in batch_df.iterrows():
                        try:
                            with engine.begin() as conn:
                                pd.DataFrame([row]).to_sql('users', conn, if_exists='append', index=False)
                            successful_users += 1
                        except IntegrityError:
                            failed_users += 1
                            failed_emails.append(row['email'])
                else:
                    raise e

        print(f"\nUsers upload summary:")
        print(f"Successfully uploaded: {successful_users}")
        # Now handle student profiles
        print("\nProcessing student profiles...")
        successful_students = 0
        failed_students = 0
        
        # Get existing user IDs first
        with engine.connect() as conn:
            existing_user_ids = pd.read_sql("SELECT id FROM users", conn)['id'].tolist()
        
        print(f"Found {len(existing_user_ids)} existing users in database")
        
        # Filter students data to only include existing user IDs
        valid_students_df = students_df[students_df['user_id'].isin(existing_user_ids)]
        print(f"Found {len(valid_students_df)} students with matching user IDs")
        
        if not valid_students_df.empty:
            # Upload in very small batches
            batch_size = 5  # Even smaller batch size for profiles
            for i in range(0, len(valid_students_df), batch_size):
                batch_df = valid_students_df.iloc[i:i + batch_size]
                try:
                    with engine.begin() as conn:
                        batch_df.to_sql('user_profiles', conn, if_exists='append', index=False)
                    successful_students += len(batch_df)
                    print(f"Uploaded profiles batch {i//batch_size + 1}/{len(valid_students_df)//batch_size + 1}")
                except Exception as e:
                    print(f"\nError in batch {i//batch_size + 1}: {str(e)}")
                    print("Attempting row-by-row upload for this batch...")
                    
                    for _, row in batch_df.iterrows():
                        try:
                            with engine.begin() as conn:
                                pd.DataFrame([row]).to_sql('user_profiles', conn, if_exists='append', index=False)
                            successful_students += 1
                            print(f"Successfully uploaded profile for user_id {row['user_id']}")
                        except Exception as e:
                            failed_students += 1
                            print(f"Failed to upload profile for user_id {row['user_id']}: {str(e)}")
            
            print(f"\nStudent profiles upload summary:")
            print(f"Successfully uploaded: {successful_students}")
            if failed_students > 0:
                print(f"Failed to upload: {failed_students}")
        else:
            print("No valid student profiles to upload - no matching user IDs found")
        
    except Exception as e:
        print("Error occurred:", str(e))
        raise

if __name__ == "__main__":
    upload_data() 