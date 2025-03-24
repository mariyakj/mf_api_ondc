from config import on_search_collection, status_collection

async def store_on_search_response(response):
    """Stores the on_search response in MongoDB and updates status"""
    transaction_id = response["context"]["transaction_id"]
    
    # Store response in MongoDB
    await on_search_collection.insert_one(response)
    
    # Update the status in MongoDB
    await update_status(transaction_id, "on_search", "completed")
    
    return {"message": "on_search response stored", "transaction_id": transaction_id}

async def update_status(transaction_id: str, stage: str, status: str):
    """Updates transaction status in MongoDB asynchronously."""
    await status_collection.update_one(
        {"transaction_id": transaction_id}, 
        {"$set": {"stage": stage, "status": status}}, 
        upsert=True
    )
