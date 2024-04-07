from fastapi import APIRouter, Form, UploadFile, File
from firebase_admin import storage
from datetime import datetime
from firebase_config import db 
from pydantic import BaseModel

router = APIRouter()

class User(BaseModel):
    email_id: str

@router.post("/user")
async def create_user(email_id: User):
    db.collection("users").document().set({"email_id" : email_id.email_id})
    return {"message": "e-mail id written succesfully"}

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    user = db.collection("users").document(user_id).get()
    if user.exists:
        return user.to_dict()
    else:
        return {"message" : "user not found"}
