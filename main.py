import os
from fastapi import FastAPI
from api.games import router as games_router
from firebase_config import db

app = FastAPI()

app.include_router(games_router)

@app.get("/")
def read_root():
    return {"Hello" : "world"}