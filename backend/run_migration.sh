#!/bin/bash
# Migration script for Supabase → Railway PostgreSQL

echo "🚀 Supabase to Railway PostgreSQL Migration"
echo "============================================="

# Check if environment file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Create .env with:"
    echo "SUPABASE_DATABASE_URL=your_supabase_connection_string"
    echo "RAILWAY_DATABASE_URL=your_railway_postgres_url"
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing migration dependencies..."
pip install sqlalchemy psycopg2-binary python-dotenv

# Run migration
echo "🔄 Starting migration..."
python migrate_to_railway.py

echo "✅ Migration script completed!"
echo ""
echo "Next steps:"
echo "1. Verify data in Railway PostgreSQL dashboard"
echo "2. Update your app to use Railway DATABASE_URL"
echo "3. Test login with migrated users"