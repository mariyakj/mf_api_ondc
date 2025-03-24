import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routes import search, on_search

app = FastAPI(title="ONDC API Client")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.head("/")
async def root():
    return {"message": "FastAPI ONDC Service Running"}

# Include routers
print("🔗 Including search router...")
app.include_router(search.router)

print("🔗 Including on_search router...")
app.include_router(on_search.router)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Render provides PORT dynamically
    print(f"Starting server on port {port}")  # Debugging statement
    uvicorn.run(app, host="0.0.0.0", port=port)
