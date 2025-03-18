import os
import time
import subprocess
import requests
import sys

CALLBACK_SERVER_URL = "http://localhost:10000"
ON_SEARCH_STATUS_URL = "https://staging.onesmf.com/check_on_search_status"
ON_SELECT_STATUS_URL = "https://staging.onesmf.com/check_on_select_status"

def is_callback_server_running():
    """Check if the callback server is already running."""
    try:
        response = requests.get(f"{CALLBACK_SERVER_URL}/status", timeout=3)
        if response.status_code == 200:
            return True
    except requests.RequestException:
        return False
    return False

def shutdown_callback_server():
    """Send a request to shut down the callback server."""
    try:
        print("Shutting down existing callback server...")
        requests.get(f"{CALLBACK_SERVER_URL}/shutdown", timeout=5)
        time.sleep(3)  # Allow time for shutdown
    except requests.RequestException:
        print("Failed to shut down the callback server.")

def wait_for_response(response_type, url):
    """Wait for a response (on_search or on_select) before proceeding."""
    print(f"Waiting for {response_type} response...")
    while True:
        try:
            response = requests.get(url)
            data = response.json()
            if data.get("status") == "received":
                print(f"{response_type} response obtained! Proceeding with next step.")
                return
        except requests.RequestException as e:
            print(f"Error checking {response_type} status: {e}")
        
        time.sleep(5)  # Check every 5 seconds

# Step 1: Ensure the callback server is not already running
if is_callback_server_running():
    print("Callback server is already running. Attempting to shut it down first.")
    shutdown_callback_server()

# Step 2: Start the callback server as a subprocess
print("Starting callback server locally on port 10000...")
callback_process = subprocess.Popen([sys.executable, "ondc-callback-server.py"])

time.sleep(5)  # Allow time for server startup

# Step 3: Run the search request
print("Running ondc_api_search.py search...")
try:
    subprocess.run([sys.executable, "ondc_api_search.py", "search"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running search: {e}")

# Step 4: Wait for `on_search` response
wait_for_response("on_search", ON_SEARCH_STATUS_URL)

# Step 5: Run the select request
print("Running ondc_api_search.py select...")
try:
    subprocess.run([sys.executable, "ondc_api_search.py", "select"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running select: {e}")

# Step 6: Wait for `on_select` response
wait_for_response("on_select", ON_SELECT_STATUS_URL)

# Step 7: Shutdown the callback server
shutdown_callback_server()

print("All API calls completed successfully.")
