release: alembic --name alembic -c backend/alembic.ini upgrade head
web: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT 