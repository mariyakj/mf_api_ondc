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

app.include_router(on_search.router, prefix="/on_search", tags=["on_search"])
logger.info("🔗 On_search router registered")

@app.on_event("startup")
async def startup_event():
    """Runs when FastAPI starts up"""
    logger.info("🚀 Starting automatic search on startup...")
    try:
        # Initialize database connection
        from services.on_search_service import client
        await client.admin.command('ping')
        logger.info("✅ MongoDB connection established")

        # Run search request once
        await search_request()
        logger.info("✅ Initial search completed")
    except Exception as e:
        logger.error(f"❌ Error in startup: {str(e)}")
        
@app.get("/")
@app.head("/")
def home():
    return {"message": "ONDC Search API is running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)