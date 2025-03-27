from fastapi import APIRouter, BackgroundTasks
from services.search_service import search_request
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/search")
async def search(background_tasks: BackgroundTasks):
    """Triggers the search process in the background"""
    try:
        response = {
            "message": "Search started",
            "status": "processing"
        }
        
        logger.info(f"🚀 API Response: {response}")  # Use logger instead of print
        
        background_tasks.add_task(search_request)
        return response

    except Exception as e:
        error_response = {"error": str(e)}
        logger.error(f"❌ Error: {error_response}")  # Use logger for errors
        return error_response