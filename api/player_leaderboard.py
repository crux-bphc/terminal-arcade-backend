from fastapi import APIRouter
from pydantic import BaseModel
from firebase_config import db
from typing import List
from google.cloud import firestore
from api.creator_leaderboard import get_user_email
from datetime import datetime
import time


router = APIRouter()

async def update_player_leaderboard(user_id: str):
    user_email = await get_user_email(user_id)
    if user_email is None:
        return {"message": "User not found"}

    leaderboard_ref = db.collection('player_leaderboard').document(user_id)
    leaderboard_entry = leaderboard_ref.get()
    current_time = datetime.now()
    if leaderboard_entry.exists:
        leaderboard_data = leaderboard_entry.to_dict()
        current_score = leaderboard_data.get('score', 0)
        new_score = current_score + 10
        leaderboard_ref.update({
            'score': new_score,
            'email': user_email,
            'updated_at': current_time
        })
    else:
        leaderboard_ref.set({
            'score': 10,
            'email': user_email,
            'updated_at': current_time
        })

class PlayerLeaderboardEntry(BaseModel):
    user_id: str
    score: int
    email: str
    updated_at: datetime


cache = {
    'player_leaderboard': [],
    'last_updated': 0
}

@router.get("/player_leaderboard", response_model=List[PlayerLeaderboardEntry])
async def get_player_leaderboard():
    current_time = time.time()
    if current_time - cache['last_updated'] > 30:
        leaderboard_ref = db.collection('player_leaderboard')
        leaderboard_entries = leaderboard_ref.order_by('score', direction = firestore.Query.DESCENDING).order_by('updated_at').stream()
        sorted_leaderboard = []
        for entry in leaderboard_entries:
            entry_data = entry.to_dict()
            sorted_leaderboard.append(PlayerLeaderboardEntry(user_id = entry.id, score = entry_data.get('score', 0), email = entry_data.get('email'), updated_at = entry_data.get('updated_at')))
        cache['player_leaderboard'] = sorted_leaderboard
        cache['last_updated'] = current_time
    return cache['player_leaderboard']