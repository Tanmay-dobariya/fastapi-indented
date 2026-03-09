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


class TodoRequest(BaseModel):
    title:str = Field(min_length=1, max_length=20)
    description:str = Field(min_length=1, max_length=100)
    priority:int = Field(ge=1, le=5)
    completed:bool = Field(default=False)


@router.get('/', status_code=status.HTTP_200_OK)
async def read_all_todos(user: user_dependency, db: db_dependency):
    todos = db.scalars(select(Todos).where(Todos.owner_id == user.get('id'))).all()
    return todos


@router.get('/{id}', status_code=status.HTTP_200_OK)
async def read_todo_by_id(user: user_dependency, db: db_dependency, id: Annotated[int, Path(gt=0)]):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

    todo = db.scalar(select(Todos).where(Todos.id == id).filter(Todos.owner_id == user.get('id')))
    
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')
    
    return todo


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

    todo = Todos(**todo_request.model_dump(), owner_id = user.get('id'))
    db.add(todo)
    db.commit()


@router.put('/update/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, id: Annotated[int, Path(gt=0)], todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

    todo = db.scalar(select(Todos).where(Todos.id == id).filter(Todos.owner_id == user.get('id')))

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')

    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.completed = todo_request.completed

    db.commit()
    db.refresh(todo)


@router.delete('/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: Annotated[int, Path(gt=0)]):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

    todo = db.scalar(select(Todos).where(Todos.id == id).filter(Todos.owner_id == user.get('id')))

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')

    db.delete(todo)
    db.commit()