
# Suggested Peers Feature

This feature uses vector embeddings (via pgvector) to match students with similar interests and backgrounds.

## How It Works

1. **Vector Embeddings**: Each user profile's text fields (interests, hobbies, etc.) are converted to vector embeddings using the Sentence Transformers library.
2. **Similarity Calculation**: These embeddings are stored in the database, and vector similarity is calculated to find the most similar profiles.
3. **Peer Suggestions**: The top 5 most similar profiles are stored and served to users through the Suggested Peers tab.

## Prerequisites

- PostgreSQL with pgvector extension installed
- Python 3.9+ with required packages

## Installation

1. **Install required packages**:
   ```bash
   pip install -r requirements_peers.txt
   ```

2. **Install pgvector extension in PostgreSQL**:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Run the database migration**:
   ```bash
   cd backend
   alembic upgrade head
   ```

## Generating Embeddings

Run the embedding generation script:

```bash
cd backend
python scripts/generate_embeddings.py
```

Options:
- `--model`: Specify a different sentence-transformer model (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `--operation`: Choose between `embeddings`, `peers`, or `refresh` (generate embeddings, find peers, or both)
- `--batch-size`: Batch size for processing (default: 100)
- `--top-n`: Number of similar peers to find (default: 5)

Example:
```bash
python scripts/generate_embeddings.py --model sentence-transformers/all-MiniLM-L6-v2 --operation refresh
```

## API Endpoints

### Get Suggested Peers

```
GET /peers/suggested
```

Returns a list of suggested peers for the current user, sorted by similarity.

Response:
```json
[
  {
    "user_id": 123,
    "name": "John Doe",
    "major": "Computer Science",
    "year": 3,
    "similarity": 0.85,
    "hobbies": "Programming, Gaming",
    "interests": "AI, Machine Learning"
  },
  ...
]
```

## Frontend

The Suggested Peers tab is available in the main navigation after login. It displays cards for each suggested peer with:

- Name and academic information
- Similarity score
- Interests and hobbies
- Option to start a conversation

## Architecture

- **Database**: PostgreSQL with pgvector extension
- **Backend**: FastAPI with SQLAlchemy ORM
- **Embedding Model**: Sentence Transformers (all-MiniLM-L6-v2)
- **Frontend**: Next.js with Tailwind CSS

## Troubleshooting

- **Missing pgvector extension**: Ensure the pgvector extension is installed in your PostgreSQL database.
- **No suggested peers showing**: Ensure embeddings have been generated with the script.
- **Performance issues**: Consider reducing the batch size or using a smaller embedding model.

## Future Improvements

- Real-time updates as profiles change
- Filter options for peer suggestions
- Explainable similarities (why users were matched)
- Notifications for new potential matches