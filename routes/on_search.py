from fastapi import APIRouter, Request
from services.on_search_service import store_on_search_response

router = APIRouter()

@router.post("/on_search")
async def on_search(request: Request):
    return await store_on_search_response(await request.json())
