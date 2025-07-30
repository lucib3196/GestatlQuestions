import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

load_dotenv()


try:
    cred = credentials.Certificate("backend_api/config/firebase_cred.json")
except Exception as e:
    raise ValueError(f"Credential file path not found {e}")

firebase_admin.initialize_app(
    cred, {"storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")}
)
db = firestore.client()
