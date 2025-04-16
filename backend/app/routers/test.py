from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["test"])

@router.get("/hello")
def test_hello():
    return {"message": "Hello from test router"} 