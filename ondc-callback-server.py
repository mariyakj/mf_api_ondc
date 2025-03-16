#ondc-callback-server.py
from flask import Flask, request, jsonify, render_template_string
import json
import os
import logging
from datetime import datetime
from pymongo import MongoClient


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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
    collection = db["on_search"]
    logging.info("Connected to MongoDB successfully.")
except Exception as e:
    logging.warning(f"MongoDB connection failed: {e}. Falling back to file storage.")

# Directory for file storage fallback
RESPONSES_DIR = "received_responses"
os.makedirs(RESPONSES_DIR, exist_ok=True)

# Extract BAP URI for display
BAP_URI = config.get("bap_uri", "")
DOMAIN = BAP_URI.replace("https://", "").replace("http://", "").split("/")[0]

@app.route("/")
def home():
    return "ONDC Callback Server is Running!"


@app.route("/on_search", methods=["POST"])
def on_search():
    try:
        request_data = request.get_json()
        transaction_id = request_data.get("context", {}).get("transaction_id", "unknown")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Store response in MongoDB if available
        if mongo_client:
            request_data["received_at"] = timestamp
            collection.insert_one(request_data)
            logging.info(f"Stored on_search response in MongoDB for transaction: {transaction_id}")
        else:
            # Fallback to file storage
            filename = f"{RESPONSES_DIR}/on_search_{transaction_id}_{timestamp.replace(':', '-')}.json"
            with open(filename, "w") as f:
                json.dump(request_data, f, indent=2)
            logging.info(f"Stored response in file: {filename}")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Error processing on_search: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/view_responses", methods=["GET"])
def view_responses():
    try:
        responses = []

        if mongo_client:
            # Fetch from MongoDB
            records = collection.find({}, {"_id": 0})  # Exclude MongoDB's `_id` field
            for data in records:
                context = data.get("context", {})
                responses.append({
                    "transaction_id": context.get("transaction_id", "unknown"),
                    "bpp_id": context.get("bpp_id", "unknown"),
                    "timestamp": context.get("timestamp", "unknown"),
                    "providers_count": len(data.get("message", {}).get("catalog", {}).get("providers", [])),
                    "items_count": sum(len(provider.get("items", [])) for provider in data.get("message", {}).get("catalog", {}).get("providers", [])),
                    "filename": context.get("transaction_id", "unknown"),  # Placeholder for file equivalent
                })
        else:
            # Fallback to File Storage
            response_files = [f for f in os.listdir(RESPONSES_DIR) if f.endswith(".json")]
            response_files.sort(reverse=True)

            for file in response_files:
                with open(os.path.join(RESPONSES_DIR, file), "r") as f:
                    data = json.load(f)
                    context = data.get("context", {})
                    responses.append({
                        "transaction_id": context.get("transaction_id", "unknown"),
                        "bpp_id": context.get("bpp_id", "unknown"),
                        "timestamp": context.get("timestamp", "unknown"),
                        "providers_count": len(data.get("message", {}).get("catalog", {}).get("providers", [])),
                        "items_count": sum(len(provider.get("items", [])) for provider in data.get("message", {}).get("catalog", {}).get("providers", [])),
                        "filename": file,
                    })

        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ONDC Responses</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                tr:hover { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>ONDC on_search Responses</h1>
            <table>
                <tr>
                    <th>Transaction ID</th>
                    <th>BPP ID</th>
                    <th>Timestamp</th>
                    <th>Providers</th>
                    <th>Items</th>
                    <th>Action</th>
                </tr>
                {% for response in responses %}
                <tr>
                    <td>{{ response.transaction_id }}</td>
                    <td>{{ response.bpp_id }}</td>
                    <td>{{ response.timestamp }}</td>
                    <td>{{ response.providers_count }}</td>
                    <td>{{ response.items_count }}</td>
                    <td><a href="/view_response/{{ response.filename }}">View Details</a></td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """, responses=responses)

    except Exception as e:
        logging.error(f"Error viewing responses: {str(e)}")
        return f"Error: {str(e)}", 500


@app.route("/view_response/<filename>", methods=["GET"])
def view_response(filename):
    try:
        if mongo_client:
            data = collection.find_one({"context.transaction_id": filename}, {"_id": 0})
            if not data:
                return "Transaction not found", 404
        else:
            filepath = os.path.join(RESPONSES_DIR, filename)
            if not os.path.exists(filepath):
                return "File not found", 404
            with open(filepath, "r") as f:
                data = json.load(f)

        formatted_json = json.dumps(data, indent=2)
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Response Details</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow: auto; }
            </style>
        </head>
        <body>
            <a href="/view_responses">← Back to All Responses</a>
            <h1>Response Details - {{ filename }}</h1>
            <pre>{{ formatted_json }}</pre>
        </body>
        </html>
        """, filename=filename, formatted_json=formatted_json)

    except Exception as e:
        logging.error(f"Error viewing response details: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Use 5000 as default
    logging.info(f"ONDC Callback Server running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
