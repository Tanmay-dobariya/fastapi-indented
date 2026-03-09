from fastapi import FastAPI
from db import engine
from models import Base
from routes import auth, todos, admin, users

app = FastAPI()
app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(todos.router, prefix='/todos', tags=['todo'])
app.include_router(admin.router, prefix='/admin', tags=['admin'])
app.include_router(users.router, prefix='/users', tags=['users'])

Base.metadata.create_all(bind=engine)
