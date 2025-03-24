from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import os

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://mariyakundukulam:xtiCnxPNdOzXvqNv@mfondc.sjcat.mongodb.net/?retryWrites=true&w=majority&appName=mfondc")
client = AsyncIOMotorClient(MONGO_URI)
DB_NAME = os.getenv("DB_NAME", "ondc_responses")



mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]

on_search_collection = db["on_search"]
status_collection = db["status"]

