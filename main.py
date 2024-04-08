from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.games import router as games_router
from api.user import router as user_router
from api.brython import router as brython_router
from api.ratings import router as ratings_router

from firebase_config import db

app = FastAPI()

origins = [
    "https://terminal-arcade.vercel.app/",
    "http://localhost:5173"  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games_router)
app.include_router(user_router)
app.include_router(brython_router)
app.include_router(ratings_router)


@app.get("/")
def read_root():
    return {"Hello": "world"}
