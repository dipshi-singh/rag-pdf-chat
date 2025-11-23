# main.py
from fastapi import FastAPI
from db import engine, Base
from auth import router as auth_router

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Auth service running!"}
