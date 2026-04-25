import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI not set")

client = MongoClient(MONGO_URI)

db = client["health_risk_db"]

users_collection = db["users"]
records_collection = db["health_records"]