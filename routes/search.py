from fastapi import APIRouter, BackgroundTasks
from services.search_service import search_request

router = APIRouter()

@router.post("/search")
async def search(background_tasks: BackgroundTasks):
    """Triggers the search process in the background without user_id"""
    try:
        response = {
            "message": "Search started",
            "status": "processing"
        }
        
        print("🚀 API Response:", response)  # Print the response to the console
        
        background_tasks.add_task(search_request)
        return response

    except Exception as e:
        error_response = {"error": str(e)}
        print("❌ Error:", error_response)  # Print errors if any
        return error_response
