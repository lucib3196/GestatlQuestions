import firebase_admin
from firebase_admin import credentials, storage
from pathlib import Path
from src.api.core import settings

# Define the credentials
if not settings.FIREBASE_PATH:
    raise ValueError("Firebase Credentials Not Found")

cred = credentials.Certificate(Path(settings.FIREBASE_PATH).resolve())
firebase_admin.initialize_app(cred, {"storageBucket": settings.STORAGE_BUCKET})

bucket = storage.bucket()
