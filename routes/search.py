import logging
from fastapi import APIRouter, BackgroundTasks
from services.search_service import perform_search

# Enable logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Debug message when the router is loaded
print("✅ search.py loaded")

router = APIRouter()

@router.post("/search") 
async def search(background_tasks: BackgroundTasks, transaction_id: str):
    """Triggers the search process in the background"""
    try:
        print(f"📢 Received /search request with transaction_id: {transaction_id}")
        logger.info(f"🔍 Search initiated for transaction_id: {transaction_id}")

        # Add search task to background tasks
        background_tasks.add_task(perform_search, transaction_id)

        return {
            "message": "Search started",
            "transaction_id": transaction_id,
            "status": "processing"
        }

    except Exception as e:
        print(f"❌ Error in /search: {e}")
        logger.error(f"❌ Error initiating search: {e}")
        return {
            "message": "Error starting search",
            "transaction_id": transaction_id,
            "status": "error",
            "error": str(e)
        }
