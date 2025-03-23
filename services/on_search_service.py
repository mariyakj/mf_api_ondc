from config import on_search_collection
from utils.redis_helper import update_status

async def store_on_search_response(response):
    transaction_id = response["context"]["transaction_id"]
    
    on_search_collection.insert_one(response)
    update_status(transaction_id, "completed")
    
    return {"message": "on_search response stored", "transaction_id": transaction_id}
