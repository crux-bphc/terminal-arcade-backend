import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'terminalarcade-e6910.appspot.com'
})

db = firestore.client()