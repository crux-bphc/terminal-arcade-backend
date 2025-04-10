from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import (
    HTTPBearer,
)

from api.games import router as games_router
from api.login import router as login_router
from api.brython import router as brython_router
from api.ratings import router as ratings_router
from api.creator_leaderboard import router as creator_leaderboard
from api.player_leaderboard import router as player_leaderboard
from models import create_db_and_init


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_db_and_init()
    yield


app = FastAPI(lifespan=lifespan, root_path="/api")

origins = [
    "https://terminal-arcade.crux-bphc.com",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


os.makedirs("game_files", exist_ok=True)
app.mount(
    "/game_files",
    StaticFiles(directory="game_files"),
    name="game_files",
)

app.include_router(games_router)
app.include_router(login_router)
app.include_router(brython_router)
app.include_router(ratings_router)
app.include_router(creator_leaderboard)
app.include_router(player_leaderboard)
# app.middleware("http")(lambda request, call_next: auth_middleware(request, call_next))

token_extractor = HTTPBearer()


@app.get("/")
def read_root():
    return {"Hello": "world"}
