from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import Depends, HTTPException, Path, APIRouter
from db import SessionLocal
from models import Todos
from starlette import status
from pydantic import BaseModel, Field
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
async def read_all_todos(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

    todos = db.scalars(select(Todos)).all()

    return todos

@router.delete('/delete/{id}')
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

    todo_to_delete = db.scalar(Todos.id == id)

    if todo_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')

    db.delete(todo_to_delete)
    db.commit()

    