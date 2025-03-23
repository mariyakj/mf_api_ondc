from pymongo import MongoClient
import redis
import os

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://mariyakundukulam:xtiCnxPNdOzXvqNv@mfondc.sjcat.mongodb.net/?retryWrites=true&w=majority&appName=mfondc")
DB_NAME = os.getenv("DB_NAME", "ondc_responses")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]

on_search_collection = db["on_search"]

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
