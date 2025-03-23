import httpx
import asyncio
from auth import generate_auth_header
from utils.redis_helper import RedisClient

async def perform_search():
    """ Performs the search operation and updates Redis status. """
    request_body, auth_header = generate_auth_header()
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    transaction_id = request_body["context"]["transaction_id"]

    # Update Redis status using class method
    RedisClient.update_status(transaction_id, "search", "processing")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://staging.gateway.proteantech.in/search", 
            json=request_body, 
            headers=headers
        )
    
    # Update Redis status after sending request
    RedisClient.update_status(transaction_id, "search", "waiting_for_on_search")
    
    return {
        "message": "Search request sent", 
        "transaction_id": transaction_id
    }