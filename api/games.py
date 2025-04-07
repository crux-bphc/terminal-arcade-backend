from fastapi import APIRouter, Form, UploadFile, File, Request
from firebase_admin import storage
from datetime import datetime
from firebase_config import db
from pydantic import BaseModel
from api.creator_leaderboard import update_creator_leaderboard
from api.ratings import get_current_user_email
import os

GAMEFILE_SIZE_LIMIT = 30_000
router = APIRouter()
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
assert SECRET_TOKEN is not None


@router.post("/games")
async def create_game(
    request: Request,
    game_title: str = Form(...),
    game_description: str = Form(...),
    creator_id: str = Form(...),
    game_file: UploadFile = File(...),
):
    if not game_file.filename.endswith(".py"):
        return {"error": "Invalid file type. Only .py files are allowed."}

    if game_file.size > GAMEFILE_SIZE_LIMIT:
        return {
            "error": f"file is too big to be uploaded. File must must be smaller than {GAMEFILE_SIZE_LIMIT / 1000: .1} KB"
        }

    headers = request.headers
    token = headers.get("Authorization")
    assert token is not None  # should be taken care of by the middleware
    user_email = await get_current_user_email(token)
    users_ref = db.collection("users")
    users_query = users_ref.where("email_id", "==", user_email)
    users = users_query.stream()

    user = next(users, None)
    if user is None:
        return {"error": "User not found."}
    creator_id = user.id

    bucket = storage.bucket()
    base_filename, file_extension = os.path.splitext(game_file.filename)
    filename = game_file.filename
    counter = 1
    while bucket.blob(filename).exists():
        filename = f"{base_filename}_{counter}{file_extension}"
        counter += 1
    blob = bucket.blob(filename)
    blob.upload_from_string(await game_file.read())
    blob.make_public()
    game_data = {
        "title": game_title,
        "description": game_description,
        "creator_id": creator_id,
        "file": blob.public_url,
        "created_at": datetime.now(),
        "total_playtime": 0,  # in seconds
        "number_of_plays": 0,
        "total_rating": 0,
        "number_of_ratings": 0,
        "disabled": False,
    }
    db.collection("games").document().set(game_data)
    return {"message": "Game created successfully"}


@router.get("/games")
async def get_all_games():
    games = db.collection("games").stream()
    game_list = [{doc.id: doc.to_dict()} for doc in games]
    return game_list


@router.get("/games/{game_id}")
async def get_game(game_id: str):
    game = db.collection("games").document(game_id).get()
    if game.exists:
        return game.to_dict()
    else:
        return {"message": "Game not found"}


@router.get("/games/creator/{creator_id}")
async def get_games_by_creator(creator_id: str):
    games = db.collection("games").where("creator_id", "==", creator_id).stream()
    game_list = [{doc.id: doc.to_dict()} for doc in games]
    return game_list


class PlayTime(BaseModel):
    play_time: int


@router.put("/games/{game_id}/playtime")
async def update_playtime(game_id: str, play_time: PlayTime, request: Request):
    header = request.headers
    token = header.get("Authorization")
    assert token is not None
    user_email = await get_current_user_email(token)
    game_ref = db.collection("games").document(game_id)
    game = game_ref.get()
    if game.exists:
        game_data = game.to_dict()
        game_users_ref = db.collection("games").document(game_id).collection("users")
        game_users = game_users_ref.where("email_id", "==", user_email).stream()
        current_total_playtime = game_data.get("total_playtime", 0)
        new_total_playtime = current_total_playtime + play_time.play_time
        total_rating = game_data.get("total_rating", 0)
        number_of_ratings = game_data.get("number_of_ratings", 0)
        if len(list(game_users)) == 0:
            number_of_plays = game_data.get("number_of_plays", 0)
            new_number_of_plays = number_of_plays + 1
            game_ref.update({"number_of_plays": new_number_of_plays})
            game_users_ref.document().set({"email_id": user_email})
            await update_creator_leaderboard(game_id, total_rating, number_of_ratings)
        game_ref.update({"total_playtime": new_total_playtime})
        return {"message": "Playtime updated successfully"}

    else:
        return {"message": "Game not found"}


@router.put("/games/{game_id}/disable")
async def disable_game(game_id: str, secret_token: str = Form(...)):
    if secret_token != SECRET_TOKEN:
        return {"message": "Cannot toggle disable"}
    game_ref = db.collection("games").document(game_id)
    game = game_ref.get()
    if game.exists:
        current_status = game.to_dict().get("disabled", False)
        game_ref.update({"disabled": not current_status})
        return {"message": "Game disabled status toggled successfully"}
    else:
        return {"message": "Game not found"}

