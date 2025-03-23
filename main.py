import os
from fastapi import FastAPI
import redis
import uvicorn
from routes import search, on_search
from utils.redis_helper import redis_client

app = FastAPI()

# Include routes
app.include_router(search.router)
app.include_router(on_search.router)


redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
client = redis.from_url(redis_url)

@app.get("/check-redis")
async def check_redis():
    try:
        response = client.ping()
        return {"status": "✅ Redis is working!" if response else "❌ Redis ping failed!"}
    except Exception as e:
        return {"status": "❌ Redis connection failed", "error": str(e)}

@app.get("/")
def root():
    return {"message": "ONDC Mutual Fund API is running!"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Render provides PORT dynamically
    uvicorn.run(app, host="0.0.0.0", port=port)