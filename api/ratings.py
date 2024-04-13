from fastapi import APIRouter
from firebase_admin import storage
from firebase_config import db 
from pydantic import BaseModel
from api.creator_leaderboard import update_creator_leaderboard
from api.player_leaderboard import update_player_leaderboard
from fastapi import HTTPException, status
import jwt
import os
from fastapi import Request

router = APIRouter()

SECRET_KEY = os.getenv('SECRET_KEY')

class Rating(BaseModel):
    game_id: str
    rating : int

class RatingCheck(BaseModel):
    game_id: str

def check_if_rated(user_email, ratings_list):
    if ratings_list is not None:
        for _rating_doc in ratings_list:
            _rating_dict = [x for x in _rating_doc.values()][0]
            if _rating_dict["user_email"] == user_email:
                return True
    return False

async def get_current_user_email(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = ['HS256'])
        return payload.get('sub')
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid token')


@router.post("/ratings/rate")
async def rate(rating: Rating, request: Request):
    headers = request.headers
    token = headers.get('Authorization')
    user_email = await get_current_user_email(token)
    if rating.rating < 1 or rating.rating > 5:
        return {"error": "Rating must be between 1 and 5"}
    game_ref = db.collection("games").document(rating.game_id)
    ratings_ref = game_ref.collection("ratings")
    ratings = ratings_ref.stream()
    all_ratings = [{document.id: document.to_dict()} for document in ratings]
    rating_exists = check_if_rated(user_email, all_ratings)
    if rating_exists==False:
        game = game_ref.get()
        if game.exists:
            game_data = game.to_dict()
            creator_id = game_data.get("creator_id")
            users_ref = db.collection("users").where("email_id", "==", user_email)
            users = users_ref.stream()
            user = next(users, None)
            if user is None:
                return {"error": "User not found."}
            user_id = user.id
            print(user_id, " ", creator_id, " ", type(user_id), " ", type(creator_id))
            if user_id == creator_id:
                print("here")
                return {"error": "Creator of game cannot rate the game."}
            
            db.collection("games").document(rating.game_id).collection("ratings").document().set({
                "game_id": rating.game_id,
                "user_email" : user_email,
                "rating" : rating.rating
            })
            
            total_rating = game_data.get('total_rating', 0) + rating.rating
            number_of_ratings = game_data.get('number_of_ratings', 0) + 1
            game_ref.update({
                'total_rating': total_rating,
                'number_of_ratings': number_of_ratings
            })

    
            await update_creator_leaderboard(rating.game_id, total_rating, number_of_ratings)
            await update_player_leaderboard(user_email)
            return {"message": "rating written succesfully"}
        else:
            return {"message": "Game does not exist."}
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
async def rated_by_user(game_id: str, request: Request):
    headers = request.headers
    token = headers.get('Authorization')
    user_email = await get_current_user_email(token)
    game_ref = db.collection('games').document(game_id)
    game = game_ref.get()
    if not game.exists:
        return {"message": "Game not found"}
    creator_id = game.to_dict().get("creator_id")
    if creator_id is None:
        return {"message": "Creator ID not found"}
    user_ref = db.collection('users').document(creator_id)
    user = user_ref.get()
    if not user.exists:
        return {"message": "User not found"}
    if user.to_dict().get("email_id") == user_email:
        return {"message": "user has rated the game"}
    ratings_query = db.collection("games").document(game_id).collection("ratings").where('user_email', '==', user_email)
    ratings = ratings_query.stream()
    if len(list(ratings)) > 0:
        return {"message": "user has rated the game"}
    else:
        return {"message": "user has not rated the game"}