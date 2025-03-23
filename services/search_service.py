import httpx
import asyncio
from auth import generate_auth_header
from utils.redis_helper import update_status
from utils.redis_helper import RedisClient

async def perform_search():
    request_body, auth_header = generate_auth_header()
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    update_status(request_body["context"]["transaction_id"], "processing")
    
    async with httpx.AsyncClient() as client:
        response = await client.post("https://staging.gateway.proteantech.in/search", json=request_body, headers=headers)
    
    update_status(request_body["context"]["transaction_id"], "waiting_for_on_search")
    
    return {"message": "Search request sent", "transaction_id": request_body["context"]["transaction_id"]}
