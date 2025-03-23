import json
import hashlib
import time
import base64
import nacl.signing
import uuid

def generate_auth_header():
    request_body = {
        "context": {
            "location": {"country": {"code": "IND"}, "city": {"code": "*"}},
            "domain": "ONDC:FIS14",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "bap_id": "staging.onesmf.com",
            "bap_uri": "https://staging.onesmf.com",
            "transaction_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "version": "2.0.0",
            "ttl": "PT10M",
            "action": "search"
        },
        "message": {
            "intent": {
                "category": {"descriptor": {"code": "MUTUAL_FUNDS"}},
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

    # Convert request body to a JSON string (compact form)
    request_body_str = json.dumps(request_body, separators=(',', ':'))

    # Generate BLAKE-512 digest
    digest_bytes = hashlib.blake2b(request_body_str.encode(), digest_size=64).digest()
    digest_base64 = base64.b64encode(digest_bytes).decode()

    # Create signing string
    created = int(time.time())
    expires = created + 3600
    signing_string = f"(created): {created}\n(expires): {expires}\ndigest: BLAKE-512={digest_base64}"

    # Private key for Ed25519 signing (replace with actual private key)
    private_key_base64 = "9MyRGumH8I+A6EHDOqz7XcUYsAGxz7NuGO6Pi13FaR+nSJzoeOX6yjTXZc/Uib2oyHe24PADJoYtrw0Fex5kvg=="
    private_key_bytes = base64.b64decode(private_key_base64)
    signing_key = nacl.signing.SigningKey(private_key_bytes[:32])

    # Sign the string using Ed25519
    signed_bytes = signing_key.sign(signing_string.encode()).signature
    signature_base64 = base64.b64encode(signed_bytes).decode()

    # Construct the Authorization header
    auth_header = (
        f'Signature keyId="staging.onesmf.com|58072g41-8cae-2f577-b8ca-24273d9b07b3|ed25519",'
        f'algorithm="ed25519",created="{created}",expires="{expires}",'
        f'headers="(created) (expires) digest",signature="{signature_base64}"'
    )

    return request_body, auth_header
