import httpx
import logging
from fastapi import HTTPException
from utils.redis_helper import update_status
from auth import generate_auth_header

logger = logging.getLogger(__name__)

async def perform_search(transaction_id: str):
    """Handles the search request and updates status"""
    try:
        request_body, auth_header = generate_auth_header()
        
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
        
        # Update initial status
        update_status(transaction_id, "search", "processing")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://staging.gateway.proteantech.in/search", 
                json=request_body, 
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()

        # Update status after successful request
        update_status(transaction_id, "search", "waiting_for_on_search")
        
        return {
            "message": "Search request sent", 
            "transaction_id": transaction_id,
            "status": "success"
        }

    except httpx.TimeoutException:
        logger.error(f"Search request timed out for transaction {transaction_id}")
        update_status(transaction_id, "search", "error")
        raise HTTPException(status_code=504, detail="Gateway timeout")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Search request failed for transaction {transaction_id}: {str(e)}")
        update_status(transaction_id, "search", "error")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error in search for transaction {transaction_id}: {str(e)}")
        update_status(transaction_id, "search", "error")
        raise HTTPException(status_code=500, detail="Internal server error")