from fastapi import APIRouter

router = APIRouter(prefix="/welcome", tags=["Welcome"])


@router.get("/")
def welcome():
    return {"message": "Welcome to FastAuth!"}
