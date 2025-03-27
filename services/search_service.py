import json
import time
import uuid
import httpx
import base64
import logging
import hashlib
from fastapi import HTTPException
from auth import generate_auth_header

logger = logging.getLogger(__name__)

async def search_request():
    """Handles ONDC Search request."""
    try:
        # Create request body with fresh UUIDs and timestamp
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

        # Convert to JSON string without spaces
        request_body_str = json.dumps(request_body, separators=(',', ':'))
        
        # Generate BLAKE-512 digest
        digest_bytes = hashlib.blake2b(request_body_str.encode(), digest_size=64).digest()
        digest_base64 = base64.b64encode(digest_bytes).decode()

        # Generate auth header
        auth_header = generate_auth_header(digest_base64)

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header,
        }

        logger.info(f"Making request to ONDC gateway...")
        logger.debug(f"Request body: {request_body_str}")
        logger.debug(f"Authorization: {auth_header}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://staging.gateway.proteantech.in/search",
                json=request_body,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        logger.error(f"Search request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))