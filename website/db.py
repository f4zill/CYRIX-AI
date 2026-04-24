# db.py

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["health_risk_db"]

users_collection = db["users"]
records_collection = db["health_records"]