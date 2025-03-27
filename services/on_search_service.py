import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

logger = logging.getLogger(__name__)

# MongoDB connection
client = AsyncIOMotorClient("mongodb+srv://mariyakundukulam:xtiCnxPNdOzXvqNv@mfondc.sjcat.mongodb.net/?retryWrites=true&w=majority&appName=mfondc")
db = client.ondc_responses
on_search_collection = db.on_search

async def store_on_search_response(response_data: dict):
    """Stores on_search response in MongoDB"""
    try:
        # Extract transaction_id from context
        transaction_id = response_data.get("context", {}).get("transaction_id")
        
        if not transaction_id:
            raise ValueError("Missing transaction_id in response")

        # Add timestamp
        document = {
            "transaction_id": transaction_id,
            "response_data": response_data,
            "received_at": datetime.utcnow(),
            "status": "received"
        }

        # Store in MongoDB
        result = await on_search_collection.insert_one(document)
        logger.info(f"Stored on_search response with _id: {result.inserted_id}")

        # Update original search request status
        await db.search_requests.update_one(
            {"transaction_id": transaction_id},
            {"$set": {"on_search_received": True, "updated_at": datetime.utcnow()}}
        )

        return result.inserted_id

    except Exception as e:
        logger.error(f"Failed to store on_search response: {str(e)}")
        raise