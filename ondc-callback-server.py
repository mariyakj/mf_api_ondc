from flask import Flask, request, jsonify, render_template_string
import json
import os
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Directory to store received responses (temporary, will be wiped on Render restart)
RESPONSES_DIR = "received_responses"
os.makedirs(RESPONSES_DIR, exist_ok=True)

# Load configuration
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Extract BAP URI for display
bap_uri = config.get('bap_uri', '')
domain = bap_uri.replace('https://', '').replace('http://', '').split('/')[0]

# === [ ROUTE: Handle on_search Responses ] ===
@app.route('/on_search', methods=['POST'])
def on_search():
    try:
        # Get JSON request data
        request_data = request.get_json()

        # Extract transaction ID
        transaction_id = request_data.get('context', {}).get('transaction_id', 'unknown')

        # Log receipt of response
        logging.info(f"📥 Received on_search response for transaction: {transaction_id}")

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{RESPONSES_DIR}/on_search_{transaction_id}_{timestamp}.json"

        # Store response in a file
        with open(filename, 'w') as f:
            json.dump(request_data, f, indent=2)

        # Log storage location
        logging.info(f"✅ Response stored in: {filename}")

        # Return success response
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"❌ Error processing on_search: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


# === [ ROUTE: View All Stored Responses ] ===
@app.route('/view_responses', methods=['GET'])
def view_responses():
    try:
        # Get all stored response files
        response_files = [f for f in os.listdir(RESPONSES_DIR) if f.endswith('.json')]
        response_files.sort(reverse=True)  # Show newest first

        responses = []
        for file in response_files:
            with open(os.path.join(RESPONSES_DIR, file), 'r') as f:
                data = json.load(f)

                # Extract metadata from response
                context = data.get('context', {})
                transaction_id = context.get('transaction_id', 'unknown')
                bpp_id = context.get('bpp_id', 'unknown')
                timestamp = context.get('timestamp', 'unknown')

                # Count providers and items
                providers_count = 0
                items_count = 0

                catalog = data.get('message', {}).get('catalog', {})
                providers = catalog.get('providers', [])
                providers_count = len(providers)

                for provider in providers:
                    items_count += len(provider.get('items', []))

                responses.append({
                    'filename': file,
                    'transaction_id': transaction_id,
                    'bpp_id': bpp_id,
                    'timestamp': timestamp,
                    'providers_count': providers_count,
                    'items_count': items_count
                })

        # Render response list as HTML
        return render_template_string('''
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
        ''', responses=responses)

    except Exception as e:
        logging.error(f"❌ Error viewing responses: {str(e)}")
        return f"Error: {str(e)}", 500


# === [ ROUTE: View Specific Response ] ===
@app.route('/view_response/<filename>', methods=['GET'])
def view_response(filename):
    try:
        with open(os.path.join(RESPONSES_DIR, filename), 'r') as f:
            data = json.load(f)

        # Format JSON for display
        formatted_json = json.dumps(data, indent=2)

        # Render JSON details as HTML
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Response Details</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow: auto; }
                .back-button { margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="back-button">
                <a href="/view_responses">← Back to All Responses</a>
            </div>
            <h1>Response Details - {{ filename }}</h1>
            <pre>{{ formatted_json }}</pre>
        </body>
        </html>
        ''', filename=filename, formatted_json=formatted_json)

    except Exception as e:
        logging.error(f"❌ Error viewing response details: {str(e)}")
        return f"Error: {str(e)}", 500


# === [ MAIN ENTRY POINT: Render Deployment Fix ] ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Get Render-assigned port
    logging.info(f"""
    ==========================================================
    🚀 ONDC Callback Server is running on port {port}
    
    🌍 Accessible Endpoints:
    - 📩 /on_search - Receives ONDC responses
    - 📄 /view_responses - View stored responses

    📡 For callbacks, update your ONDC configuration with:
    {bap_uri}

    ==========================================================
    """)
    app.run(host="0.0.0.0", port=port)
