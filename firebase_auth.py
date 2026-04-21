import pyrebase
from firebase_config import firebase_config
from datetime import datetime
import traceback

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

def signup(email, password):
    try:
        return auth.create_user_with_email_and_password(email, password)

    except Exception as e:
        error_msg = str(e)

        if "EMAIL_EXISTS" in error_msg:
            raise ValueError("This email is already registered.")
        elif "WEAK_PASSWORD" in error_msg:
            raise ValueError("Password should be at least 6 characters.")

        raise ValueError(f"Signup failed: {error_msg}")


def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_info = auth.get_account_info(user['idToken'])

        uid = user_info['users'][0]['localId']

        return {"email": email, "uid": uid}

    except Exception as e:
        error_msg = str(e)

        if "INVALID_LOGIN_CREDENTIALS" in error_msg or "EMAIL_NOT_FOUND" in error_msg:
            raise ValueError("Wrong email or password.")

        raise ValueError(f"Login failed: {error_msg}")

def log_prompt_to_firebase(email, prompt, response, meta, chain_steps=None, uid=None):
    if not isinstance(meta, dict):
        raise ValueError("Meta must be a dictionary")
    try:
        user_id = uid if uid else email.replace(".", "_")

        # Timestamp
        timestamp = meta.get("timestamp") if meta.get("timestamp") else datetime.now().isoformat()

        # Construct data
        data = {
            "email":        email,
            "prompt":       prompt,
            "response":     response,
            "timestamp":    timestamp,
            "role":         meta.get("role"),
            "audience":     meta.get("audience"),
            "tone":         meta.get("tone"),
            "intent":       meta.get("intent"),
            "temperature":  meta.get("temperature"),
            "max_tokens":   meta.get("max_tokens"),
            "rating":       meta.get("rating"),    
            "feedback":     meta.get("feedback")
        }

        if meta.get("rating") is not None:
            data["rating"] = meta["rating"]
        if meta.get("feedback"):
            data["feedback"] = meta["feedback"]
        if chain_steps:
            data["chain"] = chain_steps

        # 🔐 Push and get the log key
        result = db.child("logs").child(user_id).push(data)
        return result["name"], timestamp  # 🔁 Return Firebase key and timestamp

    except Exception as e:
        print(f"[Firebase Log Error]: {str(e)}")
        traceback.print_exc()
        return None, None  # ❌ Failed

def update_feedback_in_firebase(user_id, log_key, rating=None, feedback=None):
    try:
        if not user_id or not log_key:
            raise ValueError("user_id and log_key are required")

        updates = {}

        if rating is not None:
            updates["rating"] = rating
        if feedback:
            updates["feedback"] = feedback

        if updates:
            db.child("logs").child(user_id).child(log_key).update(updates)

    except Exception as e:
        print(f"[Firebase Feedback Update Error]: {str(e)}")
        traceback.print_exc()
#auth.py
