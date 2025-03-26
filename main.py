import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routes import search, on_search

app = FastAPI(title="ONDC Search API")

# Include Routers
app.include_router(search.router, prefix="/search", tags=["Search"])

@app.get("/")
@app.head("/")
def home():
    return {"message": "ONDC Search API is running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Render provides PORT dynamically
    print(f"Starting server on port {port}")  # Debugging statement
    uvicorn.run(app, host="0.0.0.0", port=port)
