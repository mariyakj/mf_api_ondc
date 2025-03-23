from utils.redis_helper import update_status

async def store_on_search_response(response_data: dict):
    transaction_id = response_data.get("context", {}).get("transaction_id")
    if transaction_id:
        update_status(transaction_id, "on_search", "received")
    return {"status": "success"}