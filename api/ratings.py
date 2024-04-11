from fastapi import APIRouter, Form, UploadFile, File
from firebase_admin import storage
from datetime import datetime
from firebase_config import db 
from pydantic import BaseModel
import datetime

router = APIRouter()

class Rating(BaseModel):
    user_id: str
    game_id: str
    enjoyment : int
    difficulty: int

class RatingCheck(BaseModel):
    user_id: str
    game_id: str

def check_if_rated(user_id, ratings_list):
    if ratings_list is not None:
        for _rating_doc in ratings_list:
            _rating_dict = [x for x in _rating_doc.values()][0]
            print(_rating_dict)
            if _rating_dict["user_id"] == user_id:
                return True
    return False
                

@router.post("/ratings/rate")
async def rate(rating: Rating):
    ratings = db.collection("games").document(rating.game_id).collection("ratings").stream()
    all_ratings = [{document.id: document.to_dict()} for document in ratings]
    rating_exists = check_if_rated(rating.user_id, all_ratings)
    if rating_exists==False:
        db.collection("games").document(rating.game_id).collection("ratings").document().set({
            "game_id": rating.game_id,
            "user_id" : rating.user_id,
            "enjoyment" : rating.enjoyment,
            "difficulty" : rating.difficulty
        })
        return {"message": "rating written succesfully"}
    else:
        return {"error": "user has already rated the game"}

@router.get("/games/{game_id}/ratings")
async def fetch_ratings(game_id: str):
    ratings = db.collection("games").document(game_id).collection("ratings").stream()
    all_ratings = [{document.id: document.to_dict()} for document in ratings]
    if ratings is not None:
        return all_ratings 
    else:
        return {"message": "ratings unavailable"}
    

@router.get("/ratings/hasrated")
async def rated_by_user(ratingcheck: RatingCheck):
    ratings = db.collection("games").document(ratingcheck.game_id).collection("ratings").stream()
    all_ratings = [{document.id: document.to_dict()} for document in ratings]
    rating_exists = check_if_rated(ratingcheck.user_id, all_ratings)
    if rating_exists:
        return {"message": "user has rated the game"}
    else:
        return {"message": "user has not rated the game"}