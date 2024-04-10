from fastapi import APIRouter, Form, UploadFile, File
from firebase_admin import storage
from datetime import datetime
from firebase_config import db
from pydantic import BaseModel

GAMEFILE_SIZE_LIMIT = 20_000
router = APIRouter()

import os


@router.post("/games")
async def create_game(
    game_title: str = Form(...),
    game_description: str = Form(...),
    creator_id: str = Form(...),
    game_file: UploadFile = File(...),
):
    if not game_file.filename.endswith(".py"):
        return {"error": "Invalid file type. Only .py files are allowed."}

    if game_file.size > GAMEFILE_SIZE_LIMIT:
        return {
            "error": "file is too big to be uploaded. File must must be smaller than 20KB"
        }

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
async def update_playtime(game_id: str, play_time: PlayTime):
    game_ref = db.collection("games").document(game_id)
    game = game_ref.get()
    if game.exists:
        game_data = game.to_dict()
        current_total_playtime = game_data.get("total_playtime", 0)
        number_of_plays = game_data.get("number_of_plays", 0)
        new_total_playtime = current_total_playtime + play_time.play_time
        new_number_of_plays = number_of_plays + 1
        game_ref.update(
            {
                "total_playtime": new_total_playtime,
                "number_of_plays": new_number_of_plays,
            }
        )
        return {"message": "Total playtime updated successfully"}
    else:
        return {"message": "Game not found"}
