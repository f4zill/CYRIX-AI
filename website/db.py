from pymongo import MongoClient
from datetime import datetime
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import uuid

# =========================================
# MONGODB CONNECTION
# =========================================

client = MongoClient(
    "mongodb://localhost:27017/"
)

db = client["cyrix_db"]

# =========================================
# COLLECTIONS
# =========================================

users_collection = db["users"]

assessments_collection = db["assessments"]

predictions_collection = db["predictions"]

recommendations_collection = db["recommendations"]

analytics_collection = db["analytics"]

# =========================================
# TEST CONNECTION
# =========================================

try:

    client.admin.command("ping")

    print("\n✅ MongoDB Connected Successfully\n")

except Exception as e:

    print("\n❌ MongoDB Connection Failed\n")

    print(str(e))

# =========================================
# FIX OLD INDEX CONFLICTS
# =========================================

try:

    users_collection.drop_index(
        "user_id_1"
    )

except:
    pass

try:

    users_collection.drop_index(
        "email_1"
    )

except:
    pass

# =========================================
# CREATE INDEXES
# =========================================

users_collection.create_index(

    "user_id",

    unique=True
)

users_collection.create_index(

    "email",

    unique=True
)

predictions_collection.create_index(
    "user_id"
)

assessments_collection.create_index(
    "user_id"
)

recommendations_collection.create_index(
    "user_id"
)

# =========================================
# CREATE USER
# =========================================

def create_user(
    first_name,
    last_name,
    email,
    password,
    role="user",
    phone=None,
    profile=None,
    professional=None
):

    existing_user = users_collection.find_one({

        "email": email
    })

    if existing_user:

        raise Exception(
            "Email already exists"
        )

    user_id = str(
        uuid.uuid4()
    )

    hashed_password = generate_password_hash(
        password
    )

    user = {

        "user_id": user_id,

        "first_name": first_name,

        "last_name": last_name,

        "full_name": f"{first_name} {last_name}",

        "email": email.lower(),

        "password": hashed_password,

        "role": role,

        "phone": phone,

        "profile": profile or {},

        "professional": professional or {},

        "created_at": datetime.utcnow()
    }

    users_collection.insert_one(
        user
    )

    # Remove sensitive fields before returning
    user.pop("password", None)
    user.pop("_id", None)

    return user

# =========================================
# LOGIN USER
# =========================================

def login_user(
    email,
    password
):

    user = users_collection.find_one({

        "email": email.lower()
    })

    if not user:

        return None

    password_valid = check_password_hash(

        user["password"],

        password
    )

    if not password_valid:

        return None

    user.pop("password", None)
    user.pop("_id", None)

    return user

# =========================================
# SAVE ASSESSMENT
# =========================================

def save_assessment(
    user_id,
    input_data
):

    assessment = {

        "user_id": user_id,

        "input_data": input_data,

        "timestamp": datetime.utcnow()
    }

    assessments_collection.insert_one(
        assessment
    )

# =========================================
# SAVE PREDICTION
# =========================================

def save_prediction(
    user_id,
    prediction
):

    prediction_data = {

        "user_id": user_id,

        "prediction": prediction,

        "timestamp": datetime.utcnow()
    }

    predictions_collection.insert_one(
        prediction_data
    )

# =========================================
# SAVE RECOMMENDATIONS
# =========================================

def save_recommendations(
    user_id,
    recommendations
):

    recommendation_data = {

        "user_id": user_id,

        "recommendations": recommendations,

        "timestamp": datetime.utcnow()
    }

    recommendations_collection.insert_one(
        recommendation_data
    )

# =========================================
# SAVE ANALYTICS
# =========================================

def save_analytics(
    analytics_data
):

    analytics_data["timestamp"] = datetime.utcnow()

    analytics_collection.insert_one(
        analytics_data
    )

# =========================================
# GET USER HISTORY
# =========================================

def get_user_history(
    user_id
):

    history = list(

        predictions_collection.find(

            {"user_id": user_id},

            {"_id": 0}
        )

    )

    return history

# =========================================
# GET USER ASSESSMENTS
# =========================================

def get_user_assessments(
    user_id
):

    assessments = list(

        assessments_collection.find(

            {"user_id": user_id},

            {"_id": 0}
        )

    )

    return assessments

# =========================================
# GET USER PROFILE
# =========================================

def get_user_by_id(
    user_id
):

    user = users_collection.find_one({

        "user_id": user_id

    })

    if user:

        user.pop("_id", None)

        user.pop("password", None)

    return user

# =========================================
# UPDATE USER PROFILE
# =========================================

def update_user_profile(
    user_id,
    updated_data
):

    users_collection.update_one(

        {"user_id": user_id},

        {
            "$set": updated_data
        }
    )

    return get_user_by_id(user_id)

# =========================================
# DELETE USER
# =========================================

def delete_user(
    user_id
):

    users_collection.delete_one({

        "user_id": user_id
    })

    assessments_collection.delete_many({

        "user_id": user_id
    })

    predictions_collection.delete_many({

        "user_id": user_id
    })

    recommendations_collection.delete_many({

        "user_id": user_id
    })

# =========================================
# GET ALL USERS
# =========================================

def get_all_users():

    users = list(

        users_collection.find(

            {},

            {
                "_id": 0,
                "password": 0
            }
        )

    )

    return users

# =========================================
# DATABASE HEALTH CHECK
# =========================================

def database_health():

    return {

        "mongodb_connected": True,

        "database_name": "cyrix_db",

        "users_count": users_collection.count_documents({}),

        "predictions_count": predictions_collection.count_documents({}),

        "assessments_count": assessments_collection.count_documents({})
    }