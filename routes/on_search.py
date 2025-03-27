from fastapi import APIRouter, Request, BackgroundTasks, HTTPException

from services.on_search_service import store_on_search_response

router = APIRouter()

@router.post("/on_search")
async def on_search(request: Request, background_tasks: BackgroundTasks):
    try:
        # Check if request body exists
        if request.headers.get("content-length") == "0":
            raise HTTPException(status_code=400, detail="Empty request body")

        response_data = await request.json()

        # Validate required fields
        if "context" not in response_data or "transaction_id" not in response_data["context"]:
            raise HTTPException(status_code=400, detail="Missing 'context' or 'transaction_id' in request body")

        # Process response in the background
        background_tasks.add_task(store_on_search_response, response_data)

        return {"message": "on_search response processing", "transaction_id": response_data["context"]["transaction_id"]}
    
    except Exception as e:
        return {"error": str(e)}
