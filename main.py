import os
from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials, firestore

app = FastAPI()

cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)


db = firestore.client()

@app.get("/")
def read_root():
    return {"Hello" : "world"}