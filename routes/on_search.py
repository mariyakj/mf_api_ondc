from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from typing import Dict, Any
import logging
from services.on_search_service import store_on_search_response
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

# Define response model
class OnSearchContext(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier")
    message_id: str = Field(..., description="Unique message identifier")
    action: str = Field(..., description="Action type")
    timestamp: str = Field(..., description="ISO timestamp")

class OnSearchResponse(BaseModel):
    context: OnSearchContext
    message: Dict[str, Any]

router = APIRouter(tags=["callbacks"])

@router.post("/on_search", response_model=Dict[str, str])
async def on_search(request: Request, background_tasks: BackgroundTasks):
    """
    Handle ONDC on_search callbacks
    
    Args:
        request: FastAPI Request object
        background_tasks: FastAPI BackgroundTasks object
    
    Returns:
        Dict with message and transaction_id
    
    Raises:
        HTTPException: For validation or processing errors
    """
    try:
        # Validate request content
        if request.headers.get("content-length") == "0":
            logger.error("Empty request body received")
            raise HTTPException(
                status_code=400,
                detail="Empty request body"
            )

        # Parse and validate JSON
        try:
            response_data = await request.json()
            validated_data = OnSearchResponse(**response_data)
            logger.info(f"Received on_search callback for transaction: {validated_data.context.transaction_id}")
        except ValueError as e:
            logger.error(f"Invalid JSON received: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON format: {str(e)}"
            )

        # Add to background tasks
        background_tasks.add_task(
            store_on_search_response,
            response_data
        )
        logger.info(f"Added response to background processing queue: {validated_data.context.transaction_id}")

        return {
            "message": "on_search response accepted",
            "transaction_id": validated_data.context.transaction_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing on_search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )