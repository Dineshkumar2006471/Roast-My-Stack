import os
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Firebase Admin
cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON_PATH")

if not firebase_admin._apps:
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback to Application Default Credentials
        firebase_admin.initialize_app()
    
db = firestore.client()

def get_db():
    return db

def verify_token(id_token: str):
    if not firebase_admin._apps:
        return None
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None
