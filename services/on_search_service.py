from config import on_search_collection, status_collection

async def store_on_search_response(response):
    transaction_id = response["context"]["transaction_id"]
    
    # Store the response in MongoDB
    on_search_collection.insert_one(response)
    
    # Update the status in MongoDB instead of Redis
    status_collection.update_one(
        {"transaction_id": transaction_id}, 
        {"$set": {"status": "completed"}}, 
        upsert=True
    )
    
    return {"message": "on_search response stored", "transaction_id": transaction_id}
