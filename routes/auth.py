from jose import JWTError
from datetime import timedelta, datetime, timezone
from typing import Annotated
from db import SessionLocal
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from starlette import status
from models import User
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import select
from jose import jwt


router = APIRouter()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')
SECRET_KEY = '8f1077cd0f5b347ddfa389c27406c8d7094e3a59fb4bded6a91725fbd42f5c75' # This is just a demo one you can generate your own
ALGORITHM = 'HS256'


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    create_user_model = User(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True,
        role = create_user_request.role
    )

    db.add(create_user_model)
    db.commit()


def authenticate_user(username: str, password: str, db: db_dependency):
    existing_user = db.scalar(select(User).where(User.username == username))

    if existing_user is None:
        return False
    
    if not bcrypt_context.verify(password, existing_user.hashed_password):
        return False
    
    return existing_user

def create_token(username: str, user_id: str, role: str, expires_delta = timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        user_role: str = payload.get('role')

        if username is None or user_id is None or user_role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
        
@router.post('/login', status_code=status.HTTP_200_OK, response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    token = create_token(form_data.username, user.id, user.role, timedelta(minutes=30))

    return {'access_token': token, 'token_type': 'bearer'}