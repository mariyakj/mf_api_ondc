import httpx
from pymongo import MongoClient
from auth import generate_auth_header

# Initialize MongoDB connection
client = MongoClient("mongodb+srv://mariyakundukulam:xtiCnxPNdOzXvqNv@mfondc.sjcat.mongodb.net/?retryWrites=true&w=majority&appName=mfondc")  # Replace with actual MongoDB URI
db = client["ondc_responses"]
status_collection = db["search_status"]

async def perform_search(transaction_id: str):
    """Handles the search request and updates status in MongoDB"""
    request_body, auth_header = generate_auth_header()
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    # Update status in MongoDB
    status_collection.update_one(
        {"transaction_id": transaction_id}, 
        {"$set": {"status": "processing"}}, 
        upsert=True
    )

    async with httpx.AsyncClient() as client:
        response = await client.post("https://staging.gateway.proteantech.in/search", json=request_body, headers=headers)

    # Update status after sending request
    status_collection.update_one(
        {"transaction_id": transaction_id}, 
        {"$set": {"status": "waiting_for_on_search"}}
    )

    return {"message": "Search request sent", "transaction_id": transaction_id}
