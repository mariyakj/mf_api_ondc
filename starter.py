import os
import time
import subprocess
import requests
import sys

def wait_for_response(response_type, url):
    """Wait until the response for the given type is received."""
    print(f"Waiting for {response_type} response...")
    while True:
        try:
            response = requests.get(url)
            data = response.json()
            if data.get("status") == "received":
                print(f"{response_type} response received.")
                return
        except requests.RequestException as e:
            print(f"Error checking {response_type} status: {e}")
        
        time.sleep(5)  # Check every 5 seconds

# Step 1: Start the callback server as a subprocess
port = os.environ.get("PORT", "5000")
print(f"Starting callback server locally on port {port}...")
callback_process = subprocess.Popen([sys.executable, "ondc-callback-server.py"])
callback_pid = callback_process.pid  # Get process ID for later termination

time.sleep(5)  # Allow server time to start

# Step 2: Run the search request
print("Running ondc_api_search.py search...")
try:
    subprocess.run([sys.executable, "ondc_api_search.py", "search"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running search: {e}")

# Step 3: Wait for `on_search` response
wait_for_response("on_search", "https://staging.onesmf.com/check_on_search_status")

# Step 4: Run the select request
print("Running ondc_api_search.py select...")
try:
    subprocess.run([sys.executable, "ondc_api_search.py", "select"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running select: {e}")

# Step 5: Wait for `on_select` response
wait_for_response("on_select", "https://staging.onesmf.com/check_on_select_status")

# Step 6: Shutdown the callback server once `on_select` is received
print("Shutting down callback server...")
requests.get(f"http://localhost:{port}/shutdown")  # Call Flask shutdown endpoint

# Kill the process manually in case the shutdown request fails
if callback_process.poll() is None:  
    callback_process.terminate()  # Stop the process if still running

print("All API calls completed successfully.")
