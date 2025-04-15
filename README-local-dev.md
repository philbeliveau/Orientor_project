# Local Development Setup for OaSIS Vector Search

This guide will help you set up a local development environment for the OaSIS Vector Search project, which integrates:

1. A Next.js frontend on http://localhost:3000
2. A FastAPI backend on http://localhost:8000
3. Pinecone for vector embeddings
4. OpenAI for generating embeddings
5. PostgreSQL for data storage (optional for this setup)

## Prerequisites

- Python 3.9+
- Node.js 18+
- Pinecone account (free tier works)
- OpenAI API key
- PostgreSQL (optional)

## Environment Setup

Ensure you have the following environment variables in your `.env` files:

### Backend (./backend/.env)

```
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment (e.g., gcp-starter)

# Database Configuration (optional)
LOCAL_DATABASE_URL=postgresql://postgres:password@localhost:5432/orientor_db
```

### Frontend (./frontend/.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Step 1: Prepare Pinecone

1. Sign up for a Pinecone account if you don't have one already
2. Create an index named "oasis-index" with dimension=1536 (for text-embedding-ada-002)
3. Note your API key and environment

## Step 2: Embed OaSIS Data

1. Install the required Python packages:

```bash
cd backend
pip install -r requirements.txt
```

2. Run the embedding script:

```bash
cd ..
python scripts/embed_oasis.py
```

This script will:
- Read the OaSIS CSV data
- Create embeddings using OpenAI
- Upload these embeddings to Pinecone

## Step 3: Start the Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Step 4: Start the Frontend Server

```bash
cd frontend
npm install
npm run dev
```

## Step 5: Access the Application

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Testing the Vector Search

1. Navigate to http://localhost:3000/vector-search
2. Enter a search term related to occupations, skills, or job duties
3. View the matching results from the OaSIS database

## Troubleshooting

### API Connection Issues

- Ensure CORS is properly configured in the backend
- Check that environment variables are correctly set
- Verify that Pinecone index has been populated with embeddings

### Embedding Issues

- Check OpenAI API key validity
- Ensure CSV path is correct
- Verify that the embedding process completed successfully

### No Results from Search

- Check that the embedding process completed successfully
- Verify that Pinecone query is using the same embedding model
- Try different search terms

## Next Steps

- Integrate PostgreSQL for user data storage
- Add authentication
- Implement more advanced search features
- Optimize embedding strategy for better results 