from fastapi import APIRouter, HTTPException, status, Depends
from . import service, security, models

router = APIRouter(prefix="/api", tags=["api"])

@router.post("/register")
def register(user: models.CreateUser) -> str:
    service.User.create_user(user.username, user.password, user.confirm_password)
    return "User created successfully!"

@router.post("/login")
def login(user: models.LoginUser) -> models.Token:
    login_user = service.User.check_user(user.username, user.password)
    token = security.create_jwt_token({"user_id": login_user[0]})
    return models.Token(id = login_user[0], username = login_user[1], token = token)
        
@router.get("/me")
def me(user_id: int = Depends(security.get_user)) -> models.User:
    reading_list = service.ReadingList(user_id)
    user = service.User.get_user(user_id)
    user.total_books = len(reading_list.books)
    user.reads = len(reading_list.read_books())
    return user