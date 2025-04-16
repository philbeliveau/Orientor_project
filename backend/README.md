# Orientor API - Backend

## Starting the Server

There are three ways to start the server:

### 1. Using the run.py script (Recommended)

This method ensures proper Python path configuration:

```bash
cd backend
python run.py
```

### 2. Using start_server.py

This also ensures proper path configuration and additional environment setup:

```bash
cd backend
python start_server.py
```

### 3. Using uvicorn directly 

Only works if the current directory is in the Python path:

```bash
cd backend
# Add the current directory to Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)
# Then run
uvicorn main:app --reload
```

## Common Issues

### 404 Errors for API Routes

If you're getting 404 errors for certain routes (like `/profiles/me` or `/space/recommendations`), this 
is most likely due to Python path issues. Use method #1 or #2 above to start the server properly.

### Pydantic v2 Errors

If you see error messages like:
```
Error retrieving profile: You must set the config attribute `from_attributes=True` to use from_orm
```

This is because we're using Pydantic v2 which has renamed `orm_mode` to `from_attributes` and `from_orm()` 
to `model_validate()`. These should be fixed in the codebase now. 