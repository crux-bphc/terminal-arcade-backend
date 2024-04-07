import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'techweek-terminal-arcade-69211.appspot.com'
})

db = firestore.client()