from fastapi import APIRouter, Request, HTTPException
import logging
from services.on_search_service import store_on_search_response

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/on_search")
async def on_search_callback(request: Request):
    """Handles on_search callbacks from ONDC gateway"""
    try:
        # Validate request
        if request.headers.get("content-length") == "0":
            raise HTTPException(status_code=400, detail="Empty request body")

        # Get request body
        data = await request.json()
        logger.info(f"Received on_search callback with transaction_id: {data.get('context', {}).get('transaction_id')}")

        # Store response in database
        await store_on_search_response(data)
        
        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error processing on_search callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))