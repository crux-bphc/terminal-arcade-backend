from fastapi import APIRouter
from pydantic import BaseModel
from firebase_config import db
from typing import List
from google.cloud import firestore
import math
from fastapi import HTTPException

router = APIRouter()

K = 2

async def get_user_email(user_id: str):
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    if user.exists:
        return user.to_dict().get('email_id')
    else:
        return None

def calculate_score(total_playtime: int, number_of_plays: int, total_rating: int, number_of_ratings: int, overall_average_playtime: int, max_average_playtime: int, min_average_playtime: int):
    average_game_playtime = total_playtime / number_of_plays
    average_game_rating = total_rating / number_of_ratings
    try:
        score = (K * math.log(number_of_plays) * math.pow(average_game_rating, 1.25)) / (abs(average_game_playtime - overall_average_playtime) + (max_average_playtime - min_average_playtime))
        return round(score * 100)
    except ZeroDivisionError:
        raise HTTPException(status_code = 400, detail="Division by zero error")
    except Exception as e:
        raise HTTPException(status_code = 500, detail=str(e))

class LeaderboardEntry(BaseModel):
    game_id: str
    score: int

async def update_creator_leaderboard(game_id: str, total_rating: int, number_of_ratings: int, total_number_of_plays_all_games: int, total_playtime_all_games: int, max_avg_playtime: int, min_avg_playtime: int):
    if number_of_ratings == 0:
        return
    games_ref = db.collection('games')
    game = games_ref.document(game_id).get()
    if not game.exists:
        return
    game_data = game.to_dict()
    total_playtime = game_data.get('total_playtime', 0)
    number_of_plays = game_data.get('number_of_plays', 0)
    if total_number_of_plays_all_games > 5 and number_of_plays > 0:
        overall_average_playtime = total_playtime_all_games / total_number_of_plays_all_games
        score = calculate_score(total_playtime, number_of_plays, total_rating, number_of_ratings, overall_average_playtime, max_avg_playtime, min_avg_playtime)
        leaderboard_ref = db.collection('leaderboard').document(game_id)
        leaderboard_entry = leaderboard_ref.get()
        if leaderboard_entry.exists:
            leaderboard_ref.update({'score': score})
        else:
            leaderboard_ref.set({
                'game_id': game_id,
                'score': score
            })

async def update_all_leaderboard(total_playtime_all_games: int, total_number_of_plays_all_games: int, max_avg_playtime: int, min_avg_playtime: int):
    if total_number_of_plays_all_games == 0:
        return

    games_ref = db.collection('games')
    games = games_ref.stream()

    ovr_avg_playtime = total_playtime_all_games / total_number_of_plays_all_games
    for game in games:
        game_data = game.to_dict()
        total_playtime = game_data.get('total_playtime', 0)
        number_of_plays = game_data.get('number_of_plays', 0)
        total_rating = game_data.get('total_rating', 0)
        number_of_ratings = game_data.get('number_of_ratings', 0)
        if number_of_ratings > 0 and number_of_plays >= 2:
            leaderboard_score = calculate_score(total_playtime, number_of_plays, total_rating, number_of_ratings, ovr_avg_playtime, max_avg_playtime, min_avg_playtime)
            leaderboard_ref = db.collection('leaderboard').document(game.id)
            leaderboard_entry = leaderboard_ref.get()
            if leaderboard_entry.exists:
                leaderboard_ref.update({'score': leaderboard_score})
            else:
                leaderboard_ref.set({
                    'game_id': game.id,
                    'score': leaderboard_score
                })

@router.get("/creator_leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard():
    leaderboard_ref = db.collection('leaderboard')
    leaderboard_entries = leaderboard_ref.order_by('score', direction = firestore.Query.DESCENDING).stream()
    sorted_leaderboard = []
    for entry in leaderboard_entries:
        entry_data = entry.to_dict()
        sorted_leaderboard.append(LeaderboardEntry(game_id = entry_data.get('game_id'), score = entry_data.get('score', 0)))
    return sorted_leaderboard

