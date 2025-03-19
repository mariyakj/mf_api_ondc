#ondc-callback-server.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
import os
import logging
from datetime import datetime
from pymongo import MongoClient

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Load Configuration
CONFIG_FILE = "config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as config_file:
        config = json.load(config_file)
else:
    config = {}

# MongoDB Configuration
MONGO_URI = config.get("mongo_uri", "mongodb+srv://mariyakundukulam:xtiCnxPNdOzXvqNv@mfondc.sjcat.mongodb.net/?retryWrites=true&w=majority&appName=mfondc")
DB_NAME = config.get("db_name", "ondc_responses")

# Try to connect to MongoDB
mongo_client = None
try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[DB_NAME]
    on_search_collection = db["on_search"]
    on_select_collection = db["on_select"]
    logging.info("Connected to MongoDB successfully.")
except Exception as e:
    logging.warning(f"MongoDB connection failed: {e}. Falling back to file storage.")

# Directory for file storage fallback
RESPONSES_DIR = "received_responses"
os.makedirs(RESPONSES_DIR, exist_ok=True)

# Extract BAP URI for display
BAP_URI = config.get("bap_uri", "")
DOMAIN = BAP_URI.replace("https://", "").replace("http://", "").split("/")[0]

@app.get("/")
def home():
    return {"message": "ONDC Callback Server is Running!"}


@app.post("/on_search")
async def on_search(request: Request):
    try:
        request_data = await request.json()
        transaction_id = request_data.get("context", {}).get("transaction_id", "unknown")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Store response in MongoDB
        if mongo_client:
            request_data["received_at"] = timestamp
            request_data["status"] = "received"  # ✅ Add status tracking
            on_search_collection.insert_one(request_data)
            logging.info(f"Stored on_search response in MongoDB for transaction: {transaction_id}")

        return {"status": "success"}

    except Exception as e:
        logging.error(f"Error processing on_search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/check_on_search_status")
def check_on_search_status():
    latest_search_response = on_search_collection.find_one({}, sort=[("_id", -1)])
    return {"status": "received" if latest_search_response else "waiting"}


@app.post("/on_select")
async def on_select(request: Request):
    try:
        request_data = await request.json()
        transaction_id = request_data.get("context", {}).get("transaction_id", "unknown")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Store response in MongoDB if available
        if mongo_client:
            request_data["received_at"] = timestamp
            on_select_collection.insert_one(request_data)
            logging.info(f"Stored on_select response in MongoDB for transaction: {transaction_id}")
        else:
            # Fallback to file storage
            filename = f"{RESPONSES_DIR}/on_select_{transaction_id}_{timestamp.replace(':', '-')}.json"
            with open(filename, "w") as f:
                json.dump(request_data, f, indent=2)
            logging.info(f"Stored response in file: {filename}")

        return {"status": "success"}

    except Exception as e:
        logging.error(f"Error processing on_select: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/check_on_select_status")
def check_on_select_status():
    latest_select_response = on_select_collection.find_one({}, sort=[("_id", -1)])
    return {"status": "received" if latest_select_response else "waiting"}


@app.get("/view_responses", response_class=HTMLResponse)
def view_responses():
    try:
        responses = {
            "on_search": [],
            "on_select": []
        }

        if mongo_client:
            # Fetch from MongoDB
            on_search_records = on_search_collection.find({}, {"_id": 0})
            for data in on_search_records:
                context = data.get("context", {})
                responses["on_search"].append({
                    "transaction_id": context.get("transaction_id", "unknown"),
                    "bpp_id": context.get("bpp_id", "unknown"),
                    "timestamp": context.get("timestamp", "unknown"),
                    "providers_count": len(data.get("message", {}).get("catalog", {}).get("providers", [])),
                    "items_count": sum(len(provider.get("items", [])) for provider in data.get("message", {}).get("catalog", {}).get("providers", [])),
                    "filename": context.get("transaction_id", "unknown"),
                })
            on_select_records = on_select_collection.find({}, {"_id": 0})
            for data in on_select_records:
                context = data.get("context", {})
                responses["on_select"].append({
                    "transaction_id": context.get("transaction_id", "unknown"),
                    "bpp_id": context.get("bpp_id", "unknown"),
                    "timestamp": context.get("timestamp", "unknown"),
                    "selected_items_count": len(data.get("message", {}).get("order", {}).get("items", [])),
                })

        return templates.TemplateResponse("responses.html", {"request": {}, "responses": responses})

    except Exception as e:
        logging.error(f"Error viewing responses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/view_response/{transaction_id}", response_class=HTMLResponse)
def view_response(transaction_id: str):
    try:
        data = None

        if mongo_client:
            data = on_search_collection.find_one({"context.transaction_id": transaction_id}, {"_id": 0})
            if not data:
                data = on_select_collection.find_one({"context.transaction_id": transaction_id}, {"_id": 0})

        if not data and not mongo_client:
            # Check file storage fallback
            possible_files = [
                f"on_search_{transaction_id}.json",
                f"on_select_{transaction_id}.json"
            ]
            for file in possible_files:
                filepath = os.path.join(RESPONSES_DIR, file)
                if os.path.exists(filepath):
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    break

        if not data:
            raise HTTPException(status_code=404, detail="Transaction not found")

        formatted_json = json.dumps(data, indent=2)

        return templates.TemplateResponse("response_details.html", {"request": {}, "transaction_id": transaction_id, "formatted_json": formatted_json})

    except Exception as e:
        logging.error(f"Error viewing response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))  # Use 5000 as default
    logging.info(f"ONDC Callback Server running on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)