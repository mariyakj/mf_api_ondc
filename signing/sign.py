import json
import hashlib
import time
import base64
import nacl.signing
import uuid

# === Step 1: Define the Correct ONDC Request Body ===
request_body = {
    "context": {
        "location": {
            "country": {"code": "IND"},
            "city": {"code": "*"}
        },
        "domain": "ONDC:FIS14",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),  # Dynamic timestamp
        "bap_id": "staging.onesmf.com",
        "bap_uri": "https://staging.onesmf.com",
        "transaction_id": str(uuid.uuid4()),  # Unique transaction ID
        "message_id": str(uuid.uuid4()),  # Unique message ID
        "version": "2.0.0",
        "ttl": "PT10M",
        "action": "search"
    },
    "message": {
        "intent": {
            "category": {
                "descriptor": {
                    "code": "MUTUAL_FUNDS"
                }
            },
            "fulfillment": {
                "agent": {
                    "organization": {
                        "creds": [
                            {
                                "id": "ARN-190417",
                                "type": "ARN"
                            }
                        ]
                    }
                }
            },
            "tags": [
                {
                    "display": False,
                    "descriptor": {
                        "name": "BAP Terms of Engagement",
                        "code": "BAP_TERMS"
                    },
                    "list": [
                        {
                            "descriptor": {
                                "name": "Static Terms (Transaction Level)",
                                "code": "STATIC_TERMS"
                            },
                            "value": "https://buyerapp.com/legal/ondc:fis14/static_terms?v=0.1"
                        },
                        {
                            "descriptor": {
                                "name": "Offline Contract",
                                "code": "OFFLINE_CONTRACT"
                            },
                            "value": "true"
                        }
                    ]
                }
            ]
        }
    }
}

# Convert to JSON string and remove unnecessary spaces
request_body_str = json.dumps(request_body, separators=(',', ':'))
print("Request body:\n", request_body_str)

# === Step 2: Compute the BLAKE-512 Digest ===
digest_bytes = hashlib.blake2b(request_body_str.encode(), digest_size=64).digest()
digest_base64 = base64.b64encode(digest_bytes).decode()

digest_header = f"BLAKE-512={digest_base64}"
print("\nDigest Header:", digest_header)

# === Step 3: Generate Timestamp Fields ===
created = int(time.time())  # Current timestamp
expires = created + 3600    # Expiry time (1 hour later)

# === Step 4: Construct the Signing String ===
signing_string = f"(created): {created}\n(expires): {expires}\ndigest: {digest_header}"
print("\nSigning String:\n", signing_string)

# === Step 5: Load the Provided Private Key (Base64) ===
private_key_base64 = "9MyRGumH8I+A6EHDOqz7XcUYsAGxz7NuGO6Pi13FaR+nSJzoeOX6yjTXZc/Uib2oyHe24PADJoYtrw0Fex5kvg=="  # Replace with your actual key
private_key_bytes = base64.b64decode(private_key_base64)

# Ensure the private key is exactly 64 bytes
if len(private_key_bytes) != 64:
    raise ValueError("Invalid private key length")

# Convert the private key into a SigningKey object
signing_key = nacl.signing.SigningKey(private_key_bytes[:32])  # Use only the first 32 bytes for signing

# Extract the public key for verification later
verify_key = signing_key.verify_key
public_key_base64 = base64.b64encode(verify_key.encode()).decode()

# === Step 6: Sign the Signing String ===
signed_bytes = signing_key.sign(signing_string.encode()).signature
signature_base64 = base64.b64encode(signed_bytes).decode()

print("\nSignature (Base64):", signature_base64)

# === Step 7: Construct the Authorization Header ===
authorization_header = f'Signature keyId="staging.onesmf.com|58072g41-8cae-2f577-b8ca-24273d9b07b3|ed25519",' \
                       f'algorithm="ed25519",created="{created}",expires="{expires}",' \
                       f'headers="(created) (expires) digest",signature="{signature_base64}"'

print("\nAuthorization Header:\n", authorization_header)

# === Step 8: Simulate the Verification Process ===
def verify_signature(signing_string, signature_base64, public_key_base64):
    """ Verify the signed string using the provided public key. """
    try:
        # Convert base64 keys back to bytes
        public_key_bytes = base64.b64decode(public_key_base64)
        signature_bytes = base64.b64decode(signature_base64)

        # Create a verification key object
        verify_key = nacl.signing.VerifyKey(public_key_bytes)

        # Verify the signature
        verify_key.verify(signing_string.encode(), signature_bytes)
        print("\n✅ Signature is valid!")
    except nacl.exceptions.BadSignatureError:
        print("\n❌ Signature verification failed!")

# Verify the generated signature
verify_signature(signing_string, signature_base64, public_key_base64)
