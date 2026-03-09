from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import Depends, HTTPException, Path, APIRouter
from db import SessionLocal
from models import User
from starlette import status
from .auth import get_current_user


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK)
async def read_user_by_id(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

    user_to_return = db.scalar(select(User).where(User.id == user.get('id')))

    if user_to_return is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    return user_to_return
    