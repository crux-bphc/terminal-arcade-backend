from fastapi import APIRouter, Form, UploadFile, File
from firebase_admin import storage
from datetime import datetime
from firebase_config import db 
from pydantic import BaseModel

router = APIRouter()

class Rating(BaseModel):
    user_id: str
    game_id: str
    enjoyment : int
    difficulty: int

@router.post("/ratings/rate")
async def rate(rating: Rating):
    db.collection("games").document(rating.game_id).collection("ratings").document().set({
        "game_id": rating.game_id,
        "user_id" : rating.user_id,
        "enjoyment" : rating.enjoyment,
        "difficulty" : rating.difficulty
    })
    return {"message": "rating written succesfully"}

#broken for now
@router.get("/ratings")
async def fetch_ratings():
    ratings = db.collection("games").document("ratings").collection("ratings").stream()
    all_ratings = [{document.id: document.to_dict()} for document in ratings]
    if ratings is not None:
        return all_ratings 
    else:
        return {"message": "ratings unavailable"}