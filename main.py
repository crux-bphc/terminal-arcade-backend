import os
from fastapi import FastAPI

from api.games import router as games_router
from api.user import router as user_router
from api.brython import router as brython_router

from firebase_config import db

app = FastAPI()

app.include_router(games_router)
app.include_router(user_router)
app.include_router(brython_router)


@app.get("/")
def read_root():
    return {"Hello": "world"}

