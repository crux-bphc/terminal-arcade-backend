from typing import Annotated
from fastapi import APIRouter, Depends, Form, UploadFile, File, Request
from datetime import datetime

from sqlalchemy import select, update
from pydantic import BaseModel
from api.auth import get_email
from api.creator_leaderboard import update_creator_leaderboard
from sqlalchemy.ext.asyncio import AsyncSession

import os
import hashlib

from models import get_db
from models.game import DbGame
from models.user import DbUser

GAMEFILE_SIZE_LIMIT = 30_000
router = APIRouter()
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
assert SECRET_TOKEN is not None


@router.post("/games")
async def create_game(
    request: Request,
    user_email: Annotated[str, Depends(get_email)],
    db: Annotated[AsyncSession, Depends(get_db)],
    game_title: str = Form(...),
    game_description: str = Form(...),
    # creator_id: str = Form(...),
    game_file: UploadFile = File(...),
):
    if game_file.filename is None or not game_file.filename.endswith(".py"):
        return {"error": "Invalid file type. Only .py files are allowed."}

    if game_file.size is None:
        return {"error": "game file size not found"}

    if game_file.size > GAMEFILE_SIZE_LIMIT:
        return {
            "error": f"file is too big to be uploaded. File must must be smaller than {GAMEFILE_SIZE_LIMIT / 1000: .1} KB"
        }

    user = await db.get(DbUser, user_email)
    if user is None:
        return {"error": "User not found."}

    sha1 = hashlib.sha1()
    data = await game_file.read()
    sha1.update(data)
    sha1 = sha1.hexdigest()
    filename = f"game_files/{sha1}.py"

    os.makedirs("game_files", exist_ok=True)
    with open(filename, "wb") as f:
        f.write(data)

    file_url = f"{request.base_url}{filename}"

    new_game = DbGame(
        title=game_title,
        description=game_description,
        file=file_url,
        creator_email=user_email,
        created_at=datetime.now(),
        total_playtime=0,  # in seconds
        number_of_plays=0,
        total_rating=0,
        number_of_ratings=0,
        disabled=False,
    )
    db.add(new_game)
    await db.commit()

    return {"message": "Game created successfully"}


@router.get("/games")
async def get_all_games(db: Annotated[AsyncSession, Depends(get_db)]):
    games = await db.scalars(select(DbGame))
    game_list = [{game.game_id: game.to_dict()} for game in games]

    return game_list


@router.get("/games/{game_id}")
async def get_game(game_id: str, db: Annotated[AsyncSession, Depends(get_db)]):
    game = await db.get(DbGame, game_id)

    if game:
        return game.to_dict()
    else:
        return {"message": "Game not found"}


@router.get("/games/creator/{creator_email}")
async def get_games_by_creator(
    creator_email: str, db: Annotated[AsyncSession, Depends(get_db)]
):
    games = await db.scalars(
        select(DbGame).where(DbGame.creator_email == creator_email)
    )
    game_list = [{game.game_id: game.to_dict()} for game in games]
    return game_list


class PlayTime(BaseModel):
    play_time: int


@router.put("/games/{game_id}/playtime")
async def update_playtime(
    game_id: str,
    play_time: PlayTime,
    user_email: Annotated[str, Depends(get_email)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    game = await db.get(DbGame, game_id)

    if game:
        game = await db.scalar(
            select(DbGame).where(
                DbGame.game_id == game_id
                and DbGame.played_users.any(DbUser.email == user_email)
            )
        )

        if game:
            await db.execute(
                update(DbGame)
                .where(DbGame.game_id == game_id)
                .values(number_of_plays=DbGame.number_of_plays + 1)
            )
            await db.execute(game.add_played_user(user_email))

            await update_creator_leaderboard(
                db, game_id, game.total_rating, game.number_of_ratings
            )

        await db.execute(
            update(DbGame)
            .where(DbGame.game_id == game_id)
            .values(total_playtime=DbGame.total_playtime + play_time.play_time)
        )

        await db.commit()

        return {"message": "Playtime updated successfully"}

    else:
        return {"message": "Game not found"}


@router.put("/games/{game_id}/disable")
async def disable_game(
    game_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    secret_token: str = Form(...),
):
    assert SECRET_TOKEN is not None
    if secret_token != SECRET_TOKEN:
        return {"message": "Cannot toggle disable"}

    await db.execute(
        update(DbGame)
        .where(DbGame.game_id == game_id)
        .values(disabled=DbGame.disabled.bitwise_not())
    )
    await db.commit()
