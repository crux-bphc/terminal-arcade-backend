from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel
from firebase_config import db
from typing import List
from google.cloud import firestore
from datetime import datetime


router = APIRouter()


async def update_player_leaderboard(user_email: Optional[str]):
    if user_email is None:
        return {"message": "User not found"}

    leaderboard_query = db.collection("player_leaderboard").where(
        "email", "==", user_email
    )
    leaderboard_entries = list(leaderboard_query.stream())
    current_time = datetime.now()

    if leaderboard_entries:
        leaderboard_entry = leaderboard_entries[0]
        leaderboard_ref = db.collection("player_leaderboard").document(
            leaderboard_entry.id
        )
        leaderboard_data = leaderboard_entry.to_dict()
        assert leaderboard_data is not None
        current_score = leaderboard_data.get("score", 0)
        new_score = current_score + 10
        leaderboard_ref.update(
            {"score": new_score, "email": user_email, "updated_at": current_time}
        )
    else:
        leaderboard_ref = db.collection("player_leaderboard").document()
        leaderboard_ref.set(
            {"score": 10, "email": user_email, "updated_at": current_time}
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
async def get_player_leaderboard():
    leaderboard_ref = db.collection("player_leaderboard")
    leaderboard_entries = (
        leaderboard_ref.order_by("score", direction=firestore.Query.DESCENDING)
        .order_by("updated_at")
        .stream()
    )
    sorted_leaderboard = []
    for entry in leaderboard_entries:
        entry_data = entry.to_dict()
        sorted_leaderboard.append(
            PlayerLeaderboardEntry(
                score=entry_data.get("score", 0),
                email=entry_data.get("email"),
                updated_at=entry_data.get("updated_at"),
            )
        )
    return sorted_leaderboard

