from fastapi import APIRouter, BackgroundTasks
from services.search_service import search_request

router = APIRouter()

@router.post("/")
async def search(background_tasks: BackgroundTasks, user_id: str):
    """Triggers the search process in the background"""
    try:
        background_tasks.add_task(search_request, user_id)

        return {
            "message": "Search started",
            "user_id": user_id,
            "status": "processing"
        }

    except Exception as e:
        return {"error": str(e)}
