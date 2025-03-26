import os
import logging
from fastapi import FastAPI, logger
import uvicorn
from routes import search, on_search
from services.search_service import search_request
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ONDC Search API")

# Include Routers
app.include_router(search.router)
logger.info("🔗 Search router registered")

@app.on_event("startup")
async def startup_event():
    """Runs when FastAPI starts up"""
    logger.info("🚀 Starting automatic search on startup...")
    try:
        # Create background task for search
        asyncio.create_task(periodic_search())
    except Exception as e:
        logger.error(f"❌ Error starting automatic search: {str(e)}")

async def periodic_search():
    """Performs search periodically"""
    while True:
        try:
            logger.info("📡 Initiating automatic search...")
            await search_request()
            # Wait for 5 minutes before next search
            await asyncio.sleep(300)
        except Exception as e:
            logger.error(f"❌ Error in automatic search: {str(e)}")
            # Wait for 1 minute before retry on error
            await asyncio.sleep(60)

@app.get("/")
@app.head("/")
def home():
    return {"message": "ONDC Search API is running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)