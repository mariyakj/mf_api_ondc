from fastapi import APIRouter
from services.search_service import perform_search

router = APIRouter()

@router.post("/search")
async def search():
    return await perform_search()
