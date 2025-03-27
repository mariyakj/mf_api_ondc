import json
import hashlib
import time
import base64
import nacl.signing
import uuid
import logging
import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)

ONDC_CONFIG = {
    "GATEWAY_URL": "https://staging.gateway.proteantech.in/search",
    "PRIVATE_KEY": "9MyRGumH8I+A6EHDOqz7XcUYsAGxz7NuGO6Pi13FaR+nSJzoeOX6yjTXZc/Uib2oyHe24PADJoYtrw0Fex5kvg==",
    "KEY_ID": "staging.onesmf.com|58072g41-8cae-2f577-b8ca-24273d9b07b3|ed25519",
}

async def search_request():
    """
    Performs ONDC search request with proper authentication
    """
    try:
        # Step 1: Create request body
        request_body = {
            "context": {
                "location": {
                    "country": {"code": "IND"},
                    "city": {"code": "*"}
                },
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
                                "creds": [{"id": "ARN-190417", "type": "ARN"}]
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

        # Step 2: Generate BLAKE-512 digest
        request_body_str = json.dumps(request_body, separators=(',', ':'))
        digest_bytes = hashlib.blake2b(request_body_str.encode(), digest_size=64).digest()
        digest_base64 = base64.b64encode(digest_bytes).decode()
        digest_header = f"BLAKE-512={digest_base64}"

        # Step 3: Generate timestamps
        created = int(time.time())
        expires = created + 3600

        # Step 4: Create signing string
        signing_string = f"(created): {created}\n(expires): {expires}\ndigest: {digest_header}"

        # Step 5: Sign with private key
        private_key_bytes = base64.b64decode(ONDC_CONFIG["PRIVATE_KEY"])
        if len(private_key_bytes) != 64:
            raise ValueError("Invalid private key length")

        signing_key = nacl.signing.SigningKey(private_key_bytes[:32])
        signed_bytes = signing_key.sign(signing_string.encode()).signature
        signature_base64 = base64.b64encode(signed_bytes).decode()

        # Step 6: Create authorization header
        auth_header = (
            f'Signature keyId="{ONDC_CONFIG["KEY_ID"]}",'
            f'algorithm="ed25519",created="{created}",expires="{expires}",'
            f'headers="(created) (expires) digest",signature="{signature_base64}"'
        )

        # Step 7: Make request to ONDC gateway
        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        logger.info("Making request to ONDC gateway...")
        logger.debug(f"Request body: {request_body_str}")
        logger.debug(f"Authorization: {auth_header}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                ONDC_CONFIG["GATEWAY_URL"],
                json=request_body,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            logger.info("Search request successful")
            logger.debug(f"Response: {response.json()}")
            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Error in search request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))