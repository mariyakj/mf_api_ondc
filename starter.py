import subprocess
import os
import sys
import time

# Run the API search script
print("Running ondc_api_search.py search...")
search_process = subprocess.run([sys.executable, "ondc_api_search.py", "search"])


    
if search_process.returncode != 0:
    print("Warning: API search command exited with non-zero status")

# Get the PORT environment variable with a default value
port = os.environ.get("PORT", "5000")

# Start the Flask server with Gunicorn
print("Starting callback server with Gunicorn...")
subprocess.run(["gunicorn", "-b", f"0.0.0.0:{port}", "ondc-callback-server:app"])