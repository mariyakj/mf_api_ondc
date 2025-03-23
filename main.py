import os
from fastapi import FastAPI
import redis
import uvicorn
from redis_client import RedisClient
from routes import search, on_search
from utils.redis_helper import redis_client

app = FastAPI()

# Include routes
app.include_router(search.router)
app.include_router(on_search.router)


app.include_router(search.router)

@app.get("/")
def root():
    return {"message": "ONDC Mutual Fund API is running!"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Render provides PORT dynamically
    print(f"Starting server on port {port}")  # Debugging statement
    uvicorn.run(app, host="0.0.0.0", port=port)
