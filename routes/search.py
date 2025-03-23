from fastapi import APIRouter, BackgroundTasks
from services.search_service import perform_search

router = APIRouter()

@router.post("/search")
async def search(background_tasks: BackgroundTasks, transaction_id: str):
    """Triggers the search process in the background"""
    background_tasks.add_task(perform_search, transaction_id)
    return {"message": "Search started", "transaction_id": transaction_id}
