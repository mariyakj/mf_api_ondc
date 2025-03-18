import subprocess
import os
import sys
import time
import requests
import signal
import atexit

# Global variable to track the callback server process
callback_process = None

def cleanup():
    """Function to clean up the callback server process when the script exits"""
    global callback_process
    if callback_process:
        print("Shutting down callback server...")
        try:
            # Try graceful termination first
            callback_process.terminate()
            callback_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if termination takes too long
            callback_process.kill()
        print("Callback server shut down.")

# Register the cleanup function to be called on exit
atexit.register(cleanup)

# Handle signals to ensure clean shutdown
def signal_handler(sig, frame):
    print(f"Received signal {sig}, shutting down...")
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    global callback_process
    port = os.environ.get("PORT", "10000")  # Using 10000 as seen in your logs

    # Check if the callback server is already running
    try:
        response = requests.get(f"http://127.0.0.1:{port}/", timeout=2)
        if response.status_code == 200:
            print(f"Callback server already running on port {port}.")
            already_running = True
        else:
            already_running = False
    except requests.exceptions.RequestException:
        already_running = False

    # Start the Flask callback server if not already running
    if not already_running:
        print(f"Starting callback server locally on port {port}...")
        callback_process = subprocess.Popen([sys.executable, "ondc-callback-server.py"])
        
        # Give some time for the server to start
        time.sleep(5)
        
        # Verify the server started correctly
        try:
            response = requests.get(f"http://127.0.0.1:{port}/", timeout=5)
            if response.status_code != 200:
                print("Warning: Callback server may not have started correctly.")
        except requests.exceptions.RequestException as e:
            print(f"Error: Callback server failed to start: {e}")
            cleanup()
            sys.exit(1)

    # Function to wait for a specific response with timeout
    def wait_for_response(api_name, check_url, max_attempts=30):
        print(f"Waiting for {api_name} response...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(check_url, timeout=10)
                response.raise_for_status()
                data = response.json()

                status = data.get("status", "pending")
                print(f"Current {api_name} status: {status}")

                if status == "received":
                    print(f"{api_name} response obtained! Proceeding with next step.")
                    return True
            except requests.exceptions.RequestException as e:
                print(f"Error checking {api_name} status: {e}")
                
                # For connection errors, retry immediately
                if isinstance(e, (requests.exceptions.ConnectionError, 
                                requests.exceptions.Timeout)):
                    continue
                
            time.sleep(5)  # Wait before checking again
            
        print(f"Timeout waiting for {api_name} response after {max_attempts} attempts")
        return False

    # Run the API search script
    print("Running ondc_api_search.py search...")
    try:
        subprocess.run([sys.executable, "ondc_api_search.py", "search"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running search: {e}")
        return False

    # Use the correct URL for status checking
    search_url = f"http://127.0.0.1:{port}/check_on_search_status"
    
    # Wait for on_search with timeout
    if not wait_for_response("on_search", search_url):
        return False

    # Run the select API after receiving on_search response
    print("Running ondc_api_search.py select...")
    try:
        subprocess.run([sys.executable, "ondc_api_search.py", "select"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running select: {e}")
        return False

    # Wait for on_select with timeout
    select_url = f"http://127.0.0.1:{port}/check_on_select_status"
    if not wait_for_response("on_select", select_url):
        return False

    print("All API calls completed successfully.")
    return True

if __name__ == "__main__":
    # In development mode, run the tasks and exit
    if os.environ.get("ENV") != "production":
        success = main()
        if not success:
            print("Failed to complete all API calls.")
    else:
        # In production mode on Render, keep the script running
        # to prevent automatic restarts
        success = main()
        if success:
            print("Entering keep-alive mode to maintain the server...")
            # Keep the script running indefinitely
            try:
                # Keep the main process running but check server health periodically
                port = os.environ.get("PORT", "10000")
                while True:
                    try:
                        # Periodically check if the server is still responding
                        response = requests.get(f"http://127.0.0.1:{port}/", timeout=5)
                        if response.status_code == 200:
                            # Server is healthy, sleep and check again
                            time.sleep(60)
                        else:
                            print("Warning: Server returned non-200 status code")
                            # Restart the server if needed
                            cleanup()
                            callback_process = subprocess.Popen([sys.executable, "ondc-callback-server.py"])
                            time.sleep(5)
                    except requests.exceptions.RequestException as e:
                        print(f"Error: Server health check failed: {e}")
                        # Restart the server
                        cleanup()
                        callback_process = subprocess.Popen([sys.executable, "ondc-callback-server.py"])
                        time.sleep(5)
            except KeyboardInterrupt:
                print("Shutting down by user request...")
        else:
            print("Failed to complete API calls. Exiting.")