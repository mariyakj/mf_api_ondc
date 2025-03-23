import requests
from celery_config import celery_app
from db import search_collection, select_collection, submit_collection
from auth_utils import generate_authorization_header

BASE_URL = "https://api.ondc.com"

def send_request(endpoint, payload):
    """Send an API request with dynamic authorization header."""
    headers = {
        "Authorization": generate_authorization_header(payload),
        "Content-Type": "application/json"
    }
    response = requests.post(f"{BASE_URL}/{endpoint}", json=payload, headers=headers)
    return response.json()

@celery_app.task
def search():
    """Perform Search API call and store response."""
    search_payload = { ... }  # Construct search payload
    response = send_request("search", search_payload)
    search_collection.insert_one({"payload": search_payload, "response": response})
    return response

@celery_app.task
def select():
    """Perform Select API call based on search result."""
    search_data = search_collection.find_one({}, sort=[("_id", -1)])  # Get latest search result
    if not search_data:
        return "No search result available."
    
    select_payload = { ... }  # Construct select payload based on search_data
    response = send_request("select", select_payload)
    select_collection.insert_one({"payload": select_payload, "response": response})
    return response

@celery_app.task
def submit_form():
    """Perform Submit Form API call based on select result."""
    select_data = select_collection.find_one({}, sort=[("_id", -1)])  # Get latest select result
    if not select_data:
        return "No select result available."

    submit_payload = { ... }  # Construct submit payload based on select_data
    response = send_request("submit_form", submit_payload)
    submit_collection.insert_one({"payload": submit_payload, "response": response})
    return response
