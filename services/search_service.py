import json
import time
import uuid
import httpx
import base64
import logging
from uuid import uuid4
from fastapi import HTTPException
import hashlib
from auth import generate_auth_header
from database import transaction_collection

CONFIG = {
    "API_ENDPOINTS": {
        "SEARCH": "https://staging.gateway.proteantech.in/search"
    }
}

logger = logging.getLogger(__name__)

# Default Request Body
TEMPLATE_REQUEST_BODY = {
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

async def search_request():
    """Handles ONDC Search request."""
    transaction_id = str(uuid4()).lower()
    message_id = str(uuid4()).lower()

    request_body = {
        **TEMPLATE_REQUEST_BODY,
        "context": {
            **TEMPLATE_REQUEST_BODY["context"],
            "transaction_id": transaction_id,
            "message_id": message_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    }

    # Generate BLAKE-512 Hash
    json_body = json.dumps(request_body, separators=(',', ':'))
    hashed_body = hashlib.blake2b(json_body.encode(), digest_size=64).digest()
    base64_hashed_body = base64.b64encode(hashed_body).decode()

    # Generate auth header
    auth_header = generate_auth_header(base64_hashed_body)

    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_header,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(CONFIG["API_ENDPOINTS"]["SEARCH"], json=request_body, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error(f"Search request failed: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

