import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_db_tables():
    # Load environment variables from .env file
    if os.getenv("ENV") == "production":
        load_dotenv(".env.production")
        DATABASE_URL = os.getenv("RAILWAY_DATABASE_URL")
    else:
        load_dotenv()
        DATABASE_URL = os.getenv("LOCAL_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/orientor")
    
    logger.info(f"Connecting to database: {DATABASE_URL}")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try:
        # Connect to database
        with engine.connect() as conn:
            # Get all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            logger.info(f"Found {len(tables)} tables in the database:")
            
            # Get table info for each table
            for table in tables:
                logger.info(f"Table: {table}")
                
                # Get columns
                result = conn.execute(text(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """))
                
                columns = result.fetchall()
                logger.info(f"  Columns ({len(columns)}):")
                for col in columns:
                    col_name, data_type, is_nullable, default = col
                    nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                    default_str = f" DEFAULT {default}" if default else ""
                    logger.info(f"    - {col_name} {data_type} {nullable}{default_str}")
                
                # Get constraints (primary keys, foreign keys, unique)
                result = conn.execute(text(f"""
                    SELECT con.conname, con.contype, pg_get_constraintdef(con.oid)
                    FROM pg_constraint con
                    JOIN pg_class rel ON rel.oid = con.conrelid
                    JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
                    WHERE rel.relname = '{table}'
                    ORDER BY con.contype
                """))
                
                constraints = result.fetchall()
                if constraints:
                    logger.info(f"  Constraints ({len(constraints)}):")
                    for con in constraints:
                        con_name, con_type, con_def = con
                        con_type_str = {
                            'p': 'PRIMARY KEY',
                            'f': 'FOREIGN KEY',
                            'u': 'UNIQUE',
                            'c': 'CHECK'
                        }.get(con_type, con_type)
                        logger.info(f"    - {con_name} ({con_type_str}): {con_def}")
                
                # Get indexes
                result = conn.execute(text(f"""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = '{table}'
                    AND indexname NOT IN (
                        SELECT conname
                        FROM pg_constraint
                        JOIN pg_class ON pg_constraint.conrelid = pg_class.oid
                        WHERE pg_class.relname = '{table}'
                    )
                """))
                
                indexes = result.fetchall()
                if indexes:
                    logger.info(f"  Indexes ({len(indexes)}):")
                    for idx in indexes:
                        idx_name, idx_def = idx
                        logger.info(f"    - {idx_name}: {idx_def}")
                
                logger.info("")
    
    except Exception as e:
        logger.error(f"Error inspecting database: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("Database inspection completed")

if __name__ == "__main__":
    check_db_tables() 