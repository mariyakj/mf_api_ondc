from pymongo import MongoClient

# MongoDB Connection
MONGO_URI = "mongodb+srv://mariyakundukulam:xtiCnxPNdOzXvqNv@mfondc.sjcat.mongodb.net/?retryWrites=true&w=majority&appName=mfondc"
client = MongoClient(MONGO_URI)
db = client["ondc_responses"]  # Use your actual database name

# Collections
transaction_collection = db["search_responses"]
