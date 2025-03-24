from fastapi import APIRouter, Request, BackgroundTasks
from services.on_search_service import store_on_search_response

router = APIRouter()

@router.post("/on_search")
async def on_search(request: Request, background_tasks: BackgroundTasks):
    response_data = await request.json()
    background_tasks.add_task(store_on_search_response, response_data)
    return {"message": "on_search response processing", "transaction_id": response_data["context"]["transaction_id"]}
