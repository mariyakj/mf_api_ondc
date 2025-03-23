from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["api_responses"]  # Database
search_collection = db["search_responses"]
select_collection = db["select_responses"]
submit_collection = db["submit_responses"]
