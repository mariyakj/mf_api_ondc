import os
import sys
import time
import requests
import signal
import subprocess
from urllib.parse import urlparse

# Get port from Render environment
port = os.environ.get("PORT", "10000")

# Determine the host to use for callbacks
# In Render and most cloud environments, use 127.0.0.1 instead of localhost
host = "127.0.0.1"
base_url = f"http://{host}:{port}"

print(f"Starting FastAPI callback server on port {port}...")

# Use the correct module name - replace hyphens with underscores for Python imports
# Assuming your file is actually named "ondc_callback_server.py"
callback_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "ondc-callbackserver:app", "--host", "0.0.0.0", "--port", port],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Give some time for the server to start
print("Waiting for server to start...")
time.sleep(10)  # Increased wait time to ensure server is ready

# Function to check if server is running
def is_server_running():
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Check if server started successfully
server_started = False
for _ in range(5):  # Try 5 times
    if is_server_running():
        server_started = True
        print("Server started successfully!")
        break
    else:
        print("Server not responding yet, waiting...")
        time.sleep(5)

if not server_started:
    print("Error: Failed to start the server. Checking for error output:")
    # Capture any output from the server process
    stdout, stderr = callback_process.communicate(timeout=5)
    print(f"Server stdout: {stdout}")
    print(f"Server stderr: {stderr}")
    sys.exit(1)

# Function to wait for a specific response with timeout
def wait_for_response(api_name, check_endpoint, max_retries=30):
    print(f"Waiting for {api_name} response...")
    check_url = f"{base_url}{check_endpoint}"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(check_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "pending")
                print(f"Current {api_name} status: {status}")
                
                if status == "received":
                    print(f"{api_name} response obtained! Proceeding with next step.")
                    return True
            else:
                print(f"Got status code {response.status_code} from {check_url}")
        except requests.exceptions.RequestException as e:
            print(f"Error checking {api_name} status (attempt {attempt+1}/{max_retries}): {e}")
        
        time.sleep(5)  # Wait before checking again
    
    print(f"Timeout waiting for {api_name} response after {max_retries} attempts")
    return False

# Run the API search script
print("Running ondc_api_search.py search...")
try:
    search_process = subprocess.run(
        [sys.executable, "ondc_api_search.py", "search"], 
        check=True,
        capture_output=True,
        text=True
    )
    print("Search output:", search_process.stdout)
except subprocess.CalledProcessError as e:
    print(f"Error running search: {e}")
    print("Error output:", e.stdout)
    print("Error stderr:", e.stderr)

# Wait for on_search response
search_success = wait_for_response("on_search", "/check_on_search_status")

if search_success:
    # Run the select API after receiving on_search response
    print("Running ondc_api_search.py select...")
    try:
        select_process = subprocess.run(
            [sys.executable, "ondc_api_search.py", "select"], 
            check=True,
            capture_output=True,
            text=True
        )
        print("Select output:", select_process.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running select: {e}")
        print("Error output:", e.stdout)
        print("Error stderr:", e.stderr)

    # Wait for on_select response
    select_success = wait_for_response("on_select", "/check_on_select_status")
    
    if select_success:
        print("All API calls completed successfully.")
    else:
        print("Failed to receive on_select response in time.")
else:
    print("Failed to receive on_search response in time. Skipping select step.")

# Keep the server running in Render environment
# In Render, we want the server to keep running instead of terminating
if "RENDER" in os.environ:
    print("Running in Render environment. Keeping server alive...")
    try:
        # Wait for the server process instead of terminating it
        callback_process.wait()
    except KeyboardInterrupt:
        print("Received shutdown signal, terminating server...")
        callback_process.terminate()
else:
    # For local development, terminate as before
    print("Terminating callback server...")
    callback_process.terminate()