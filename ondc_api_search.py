import json
import hashlib
import time
import base64
import nacl.signing
import uuid
import requests
import sys  # For command-line arguments

# === Load Configuration from config.json ===
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# === Step 1: Get API Action from Command-Line Argument ===
if len(sys.argv) < 2:
    print("Usage: python script.py <search|select|init|confirm>")
    sys.exit(1)

api_action = sys.argv[1]  # e.g., "search", "select", "init", "confirm"

# Validate API action
if api_action not in config["api_endpoints"]:
    print(f"Error: Invalid API action '{api_action}'. Choose from: {', '.join(config['api_endpoints'].keys())}")
    sys.exit(1)

api_url = config["api_endpoints"][api_action]  # Get the corresponding API URL
base_payload = config["payloads"][api_action]  # Get the corresponding payload template

# === Step 2: Build Dynamic Request Body ===
request_body = {
    "context": {
        "location": base_payload["context"]["location"],
        "domain": config["domain"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),  # Dynamic timestamp
        "bap_id": config["bap_id"],
        "bap_uri": config["bap_uri"],
        "transaction_id": str(uuid.uuid4()),  # Unique transaction ID
        "message_id": str(uuid.uuid4()),  # Unique message ID
        "version": config["version"],
        "ttl": config["ttl"],
        "action": api_action
    },
    "message": base_payload["message"]  # Load message part dynamically
}

# Convert to JSON string
request_body_str = json.dumps(request_body, separators=(',', ':'))

# === Step 3: Compute the BLAKE-512 Digest ===
digest_bytes = hashlib.blake2b(request_body_str.encode(), digest_size=64).digest()
digest_base64 = base64.b64encode(digest_bytes).decode()
digest_header = f"BLAKE-512={digest_base64}"

# === Step 4: Generate Timestamp Fields ===
created = int(time.time())  # Current timestamp
expires = created + 3600    # Expiry time (1 hour later)

# === Step 5: Construct the Signing String ===
signing_string = f"(created): {created}\n(expires): {expires}\ndigest: {digest_header}"

# === Step 6: Load Private Key ===
private_key_base64 = config["private_key_base64"]
private_key_bytes = base64.b64decode(private_key_base64)

# Ensure private key length is correct
if len(private_key_bytes) != 64:
    raise ValueError("Invalid private key length")

# Convert private key into SigningKey object
signing_key = nacl.signing.SigningKey(private_key_bytes[:32])  # Use first 32 bytes for signing

# Extract public key
verify_key = signing_key.verify_key
public_key_base64 = base64.b64encode(verify_key.encode()).decode()

# === Step 7: Sign the Signing String ===
signed_bytes = signing_key.sign(signing_string.encode()).signature
signature_base64 = base64.b64encode(signed_bytes).decode()

# === Step 8: Construct Authorization Header ===
authorization_header = f'Signature keyId="{config["key_id"]}",' \
                       f'algorithm="ed25519",created="{created}",expires="{expires}",' \
                       f'headers="(created) (expires) digest",signature="{signature_base64}"'

# === Step 9: Send the request ===
headers = {
    "Content-Type": "application/json",
    "Authorization": authorization_header
}

response = requests.post(api_url, headers=headers, data=request_body_str)

# Print response
print("\nAPI Action:", api_action)
print("Request Sent to:", api_url)
print("\nResponse Status Code:", response.status_code)
print("\nResponse Body:", response.text)
