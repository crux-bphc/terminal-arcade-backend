from fastapi import APIRouter, Depends
from typing import Annotated, Optional
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from models import get_db
from models.player_leaderboard import DbPlayerLeaderBoardEntry

router = APIRouter()


async def update_player_leaderboard(db: AsyncSession, user_email: Optional[str]):
    if user_email is None:
        return {"message": "User not found"}

    current_time = datetime.now()

    await db.execute(
        insert(DbPlayerLeaderBoardEntry)
        .values(player_email=user_email, score=10, updated_at=current_time)
        .on_conflict_do_update(
            index_elements=["player_email"],
            set_={
                "score": DbPlayerLeaderBoardEntry.score + 10,
                "updated_at": current_time,
            },
        )
    )


class PlayerLeaderboardEntry(BaseModel):
    score: int
    email: str
    updated_at: datetime


cache = {"player_leaderboard": [], "last_updated": 0, "initialized": False}

# def update_player_leaderboard_cache():
#     print("updating cache")
#     current_time = time.time()
#     leaderboard_ref = db.collection('player_leaderboard')
#     leaderboard_entries = leaderboard_ref.order_by('score', direction = firestore.Query.DESCENDING).order_by('updated_at').stream()
#     sorted_leaderboard = []
#     for entry in leaderboard_entries:
#         entry_data = entry.to_dict()
#         sorted_leaderboard.append(PlayerLeaderboardEntry(score = entry_data.get('score', 0), email = entry_data.get('email'), updated_at = entry_data.get('updated_at')))
#     cache['player_leaderboard'] = sorted_leaderboard
#     cache['last_updated'] = current_time
#     cache['initialized'] = True

# async def update_player_leaderboard_periodically():
#     while True:
#         await asyncio.to_thread(update_player_leaderboard_cache)
#         await asyncio.sleep(30)

# asyncio.create_task(update_player_leaderboard_periodically())

# @router.get("/player_leaderboard", response_model=List[PlayerLeaderboardEntry])
# async def get_player_leaderboard():
#     current_time = time.time()
#     if not cache['initialized'] or current_time - cache['last_updated'] > 30:
#         await update_player_leaderboard_cache()
#     return cache['player_leaderboard']


@router.get("/player_leaderboard", response_model=List[PlayerLeaderboardEntry])
async def get_player_leaderboard(db: Annotated[AsyncSession, Depends(get_db)]):
    leaderboard_entries = await db.scalars(
        select(DbPlayerLeaderBoardEntry).order_by(
            DbPlayerLeaderBoardEntry.score.desc(), DbPlayerLeaderBoardEntry.updated_at
        )
    )
    result = [
        PlayerLeaderboardEntry(
            score=entry.score, email=entry.player_email, updated_at=entry.updated_at
        )
        for entry in leaderboard_entries
    ]
    return result
