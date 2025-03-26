import httpx
import logging
import json
from fastapi import HTTPException
from auth import generate_auth_header
from services.on_search_service import update_status  # Update status in MongoDB

logger = logging.getLogger(__name__)

async def perform_search(transaction_id: str):
    """Sends search request to ONDC and updates the status in MongoDB."""
    
    logger.info(f"🔍 perform_search() CALLED with transaction_id: {transaction_id}")

    try:
        print("📢 Calling generate_auth_header()...")  # Debugging
        request_body, auth_header = generate_auth_header()
        
        if not request_body or not auth_header:
            logger.error("❌ ERROR: Auth header or request body missing!")
            return {"error": "Auth header or request body is missing!"}

        print("✅ generate_auth_header() executed successfully!")

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }

        logger.info(f"📝 Generated Headers: {headers}")
        logger.info(f"📌 DEBUG: Generated Request Body: {json.dumps(request_body, indent=2)}")

        # Update MongoDB status before sending request
        await update_status(transaction_id, "search", "processing")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://staging.gateway.proteantech.in/search",
                json=request_body,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()  # Raise error if response is 4xx/5xx

        response_data = response.json()
        logger.info(f"✅ Search response received for {transaction_id}: {json.dumps(response_data, indent=2)}")

        # Update status in MongoDB
        await update_status(transaction_id, "search", "waiting_for_on_search")

        return {
            "message": "Search request sent",
            "transaction_id": transaction_id,
            "status": "success",
            "response": response_data
        }

    except httpx.TimeoutException:
        logger.error(f"❌ Search request timed out for transaction {transaction_id}")
        await update_status(transaction_id, "search", "error")
        raise HTTPException(status_code=504, detail="Gateway timeout")

    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Search request failed for {transaction_id}: {e.response.status_code} - {e.response.text}")
        await update_status(transaction_id, "search", "error")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    except Exception as e:
        logger.exception(f"❌ Unexpected error in search for transaction {transaction_id}: {str(e)}")
        await update_status(transaction_id, "search", "error")
        raise HTTPException(status_code=500, detail="Internal server error")
