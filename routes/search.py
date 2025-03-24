from fastapi import APIRouter, BackgroundTasks
from services.search_service import perform_search
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/search") 
async def search(background_tasks: BackgroundTasks, transaction_id: str):
    """Triggers the search process in the background"""
    try:
        # Add search task to background tasks
        background_tasks.add_task(perform_search, transaction_id)
        
        logger.info(f"Search initiated for transaction_id: {transaction_id}")
        return {
            "message": "Search started", 
            "transaction_id": transaction_id,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error initiating search: {e}")
        return {
            "message": "Error starting search",
            "transaction_id": transaction_id,
            "status": "error",
            "error": str(e)
        }