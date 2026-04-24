from db import users_collection
import uuid
from datetime import datetime

def create_user(name, email, password):
    user = {
        "user_id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "password": password,
        "created_at": datetime.utcnow()
    }
    users_collection.insert_one(user)
    return user

def login_user(email, password):
    return users_collection.find_one(
        {"email": email, "password": password},
        {"_id": 0, "user_id": 1, "name": 1}   # ← only return what app.py needs
    )