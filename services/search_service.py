import httpx
import logging
from fastapi import HTTPException
from auth import generate_auth_header
from services.on_search_service import update_status  # Import the function from on_search_service

logger = logging.getLogger(__name__)

async def perform_search(transaction_id: str):
    logger.info(f"🔍 perform_search() CALLED with transaction_id: {transaction_id}")

    try:
        print("📢 Calling generate_auth_header()...")  # Debugging
        request_body, auth_header = generate_auth_header()
        print("✅ generate_auth_header() executed successfully!")

        print(f"📌 DEBUG: Generated Request Body: {json.dumps(request_body, indent=2)}")  
        print(f"📌 DEBUG: Generated Auth Header: {auth_header}")

        if not request_body:
            print("❌ ERROR: Empty request body detected!")
            return {"error": "Empty request body detected!"}

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }

        logger.info(f"Initiating search for transaction_id: {transaction_id}")

        # Update initial status in MongoDB
        await update_status(transaction_id, "search", "processing")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://staging.gateway.proteantech.in/search",
                json=request_body,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()

        response_data = response.json()
        logger.info(f"✅ Search response received for {transaction_id}: {response_data}")

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
        logger.error(f"❌ Search request failed for transaction {transaction_id}: {e.response.status_code} - {e.response.text}")
        await update_status(transaction_id, "search", "error")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    except Exception as e:
        logger.exception(f"❌ Unexpected error in search for transaction {transaction_id}")
        await update_status(transaction_id, "search", "error")
        raise HTTPException(status_code=500, detail="Internal server error")
