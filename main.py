from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import FastAPI, Depends, HTTPException, Path
from db import engine, SessionLocal
from models import Base, Todos
from starlette import status
from pydantic import BaseModel, Field

app = FastAPI()


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title:str = Field(min_length=1, max_length=20)
    description:str = Field(min_length=1, max_length=100)
    priority:int = Field(ge=1, le=5)
    completed:bool = Field(default=False)


@app.get('/', status_code=status.HTTP_200_OK)
async def read_all_todos(db: db_dependency):
    todos = db.scalars(select(Todos)).all()
    return todos


@app.get('/todo/{id}', status_code=status.HTTP_200_OK)
async def read_todo_by_id(db: db_dependency, id: Annotated[int, Path(gt=0)]):
    todo = db.scalar(select(Todos).where(Todos.id == id))
    
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')
    
    return todo


@app.post('/todo/create', status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo = Todos(**todo_request.model_dump())
    db.add(todo)
    db.commit()


@app.put('/todo/update/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, id: Annotated[int, Path(gt=0)], todo_request: TodoRequest):
    todo = db.scalar(select(Todos).where(Todos.id == id))

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')

    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.completed = todo_request.completed

    db.commit()
    db.refresh(todo)


@app.delete('/todo/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, id: Annotated[int, Path(gt=0)]):
    todo = db.scalar(select(Todos).where(Todos.id == id))

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')

    db.delete(todo)
    db.commit()