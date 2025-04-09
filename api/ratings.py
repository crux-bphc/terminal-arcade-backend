from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi import HTTPException, status
import jwt
import os
from fastapi import Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from api.creator_leaderboard import update_creator_leaderboard
from api.player_leaderboard import update_player_leaderboard
from models import get_db
from models.game import DbGame
from models.rating import DbRating

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")


class Rating(BaseModel):
    game_id: str
    rating: int


class RatingCheck(BaseModel):
    game_id: str


async def get_current_user_email(token: str) -> str:
    try:
        assert SECRET_KEY is not None
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )


@router.post("/ratings/rate")
async def rate(
    rating: Rating, request: Request, db: Annotated[AsyncSession, Depends(get_db)]
):
    headers = request.headers
    token = headers.get("Authorization")
    assert token is not None

    user_email = await get_current_user_email(token)
    if rating.rating < 1 or rating.rating > 5:
        return {"error": "Rating must be between 1 and 5"}

    game = await db.scalar(
        select(DbGame).where(
            DbGame.game_id == rating.game_id and DbGame.creator_email != user_email
        )
    )
    if not game:
        return {"error": "No such game exists or no such game can be rated"}

    await db.execute(
        insert(DbRating).values(
            game_id=rating.game_id, player_email=user_email, rating=rating.rating
        )
    )

    result = await db.execute(
        update(DbGame)
        .where(DbGame.game_id == game.game_id)
        .values(total_rating=DbGame.total_rating + rating.rating)
        .returning(DbGame.total_rating)
    )
    total_rating = result.fetchone().tuple()[0]

    await update_creator_leaderboard(
        db, rating.game_id, total_rating, game.number_of_ratings + 1
    )
    await update_player_leaderboard(db, user_email)

    await db.commit()

    return {"message": "rating written succesfully"}


@router.get("/games/{game_id}/ratings")
async def fetch_ratings(game_id: str, db: Annotated[AsyncSession, Depends(get_db)]):
    ratings = db.collection("games").document(game_id).collection("ratings").stream()
    all_ratings = [{document.id: document.to_dict()} for document in ratings]

    game = await db.scalar(
        select(DbGame).join(DbGame.ratings).where(DbGame.game_id == game_id)
    )
    return [{rating.player_email: rating.to_dict()} for rating in game.ratings]


@router.get("/ratings/hasrated")
async def rated_by_user(
    game_id: str, request: Request, db: Annotated[AsyncSession, Depends(get_db)]
):
    headers = request.headers
    token = headers.get("Authorization")
    user_email = await get_current_user_email(token)

    rating = await db.scalar(
        select(DbRating).where(
            DbRating.game_id == game_id and DbRating.player_email == user_email
        )
    )

    return {"rated": rating is not None}
