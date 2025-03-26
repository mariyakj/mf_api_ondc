from fastapi import APIRouter, BackgroundTasks
from services.search_service import search_request

router = APIRouter()

@router.post("/")
async def search(background_tasks: BackgroundTasks):
    """Triggers the search process in the background without user_id"""
    try:
        background_tasks.add_task(search_request)

        return {
            "message": "Search started",
            "status": "processing"
        }

    except Exception as e:
        return {"error": str(e)}
