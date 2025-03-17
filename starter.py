import subprocess
import os
import sys
import time
import requests

port = os.environ.get("PORT", "5000")

# Start the Flask callback server in the background
print(f"Starting callback server locally on port {port}...")
callback_process = subprocess.Popen([sys.executable, "ondc-callback-server.py"])

# Give some time for the server to start
time.sleep(5)

# Run the API search script
print("Running ondc_api_search.py search...")
try:
    search_process = subprocess.run([sys.executable, "ondc_api_search.py", "search"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running search: {e}")

# Function to wait for a specific response
def wait_for_response(api_name, check_url):
    print(f"Waiting for {api_name} response...")
    
    while True:
        try:
            response = requests.get(check_url, timeout=10)  # Timeout to avoid hanging
            response.raise_for_status()  # Raise HTTP error if status is not 200
            data = response.json()

            status = data.get("status", "pending")
            print(f"Current {api_name} status: {status}")

            if status == "received":
                print(f"{api_name} response obtained! Proceeding with next step.")
                return  # Exit loop
        except requests.exceptions.RequestException as e:
            print(f"Error checking {api_name} status: {e}")

        time.sleep(5)  # Wait before checking again

# Wait for on_search before proceeding
wait_for_response("on_search", "https://staging.onesmf.com/check_on_search_status")

# Run the select API after receiving on_search response
print("Running ondc_api_search.py select...")
try:
    select_process = subprocess.run([sys.executable, "ondc_api_search.py", "select"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running select: {e}")

# Wait for on_select before proceeding
wait_for_response("on_select", "https://staging.onesmf.com/check_on_select_status")

# Run the on_select API after receiving on_select response
print("Running ondc_api_search.py on_select...")
try:
    on_select_process = subprocess.run([sys.executable, "ondc_api_search.py", "on_select"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running on_select: {e}")

print("All API calls completed successfully.")

# Start the Flask server with Gunicorn only in production
if os.environ.get("ENV") == "production":
    print("Starting callback server with Gunicorn...")
    subprocess.run(["gunicorn", "-b", f"0.0.0.0:{port}", "ondc-callback-server:app"])
else:
    print(f"Callback server already running on port {port}.")
