import firebase_admin
from firebase_admin import credentials, firestore
import os

storageBucket = os.getenv("STORAGE_BUCKET")

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {"storageBucket": storageBucket})

db = firestore.client()

