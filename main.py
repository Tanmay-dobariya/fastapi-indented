from fastapi import FastAPI
from db import engine
from models import Base
from routes import auth, todos

app = FastAPI()
app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(todos.router, prefix='/todos', tags=['todo'])

Base.metadata.create_all(bind=engine)
