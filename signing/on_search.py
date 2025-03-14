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
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "*"
      }
    },
    "domain": "ONDC:FIS14",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
    "bap_uri": "https://staging.onesmf.com",
    "transaction_id": str(uuid.uuid4()),
    "message_id": str(uuid.uuid4()),
    "version": "2.0.0",
    "ttl": "PT10M",
    "bpp_id": "api.sellerapp.com",
    "bpp_uri": "https://api.sellerapp.com/ondc",
    "action": "on_search"
  },
  "message": {
    "catalog": {
      "descriptor": {
        "name": "BPP Name"
      },
      "providers": [
        {
          "id": "amc_1",
          "descriptor": {
            "name": "ABC Mutual Fund"
          },
          "categories": [
            {
              "id": "0",
              "descriptor": {
                "name": "Mutual Funds",
                "code": "MUTUAL_FUNDS"
              }
            },
            {
              "id": "1",
              "descriptor": {
                "name": "Open Ended",
                "code": "OPEN_ENDED"
              },
              "parent_category_id": "0"
            },
            {
              "id": "11",
              "descriptor": {
                "name": "Equity",
                "code": "OPEN_ENDED_EQUITY"
              },
              "parent_category_id": "1"
            },
            {
              "id": "1101",
              "descriptor": {
                "name": "Mid Cap Fund",
                "code": "OPEN_ENDED_EQUITY_MIDCAP"
              },
              "parent_category_id": "11"
            }
          ],
          "items": [
            {
              "id": "138",
              "descriptor": {
                "name": "ABC Mid Cap Fund",
                "code": "SCHEME"
              },
              "category_ids": [
                "1101"
              ],
              "matched": "true",
              "tags": [
                {
                  "display": "true",
                  "descriptor": {
                    "name": "Scheme Information",
                    "code": "SCHEME_INFORMATION"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "name": "Status",
                        "code": "STATUS"
                      },
                      "value": "active"
                    },
                    {
                      "descriptor": {
                        "name": "Lockin Period (days)",
                        "code": "LOCKIN_PERIOD_IN_DAYS"
                      },
                      "value": "365"
                    },
                    {
                      "descriptor": {
                        "name": "NFO Start",
                        "code": "NFO_START_DATE"
                      },
                      "value": "2024-07-25"
                    },
                    {
                      "descriptor": {
                        "name": "NFO End",
                        "code": "NFO_END_DATE"
                      },
                      "value": "2024-08-10"
                    },
                    {
                      "descriptor": {
                        "name": "NFO Allotment Date",
                        "code": "NFO_ALLOTMENT_DATE"
                      },
                      "value": "2024-08-15"
                    },
                    {
                      "descriptor": {
                        "name": "NFO Reopen Date",
                        "code": "NFO_REOPEN_DATE"
                      },
                      "value": "2024-08-16"
                    },
                    {
                      "descriptor": {
                        "name": "Entry Load",
                        "code": "ENTRY_LOAD"
                      },
                      "value": "no entry load"
                    },
                    {
                      "descriptor": {
                        "name": "Exit Load",
                        "code": "EXIT_LOAD"
                      },
                      "value": "1% on exit"
                    },
                    {
                      "descriptor": {
                        "name": "Scheme Offer Documents",
                        "code": "OFFER_DOCUMENTS"
                      },
                      "value": "https://sellerapp.com/docs/scheme-offer.pdf"
                    }
                  ]
                }
              ]
            },
            {
              "id": "12391",
              "descriptor": {
                "name": "ABC Mid Cap Fund - Regular - Growth",
                "code": "SCHEME_PLAN"
              },
              "category_ids": [
                "1101"
              ],
              "parent_item_id": "138",
              "fulfillment_ids": [
                "ff_122",
                "ff_123",
                "ff_124",
                "ff_125"
              ],
              "matched": "true",
              "tags": [
                {
                  "display": "true",
                  "descriptor": {
                    "name": "Plan Information",
                    "code": "PLAN_INFORMATION"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "name": "Consumer Terms & Conditions",
                        "code": "CONSUMER_TNC"
                      },
                      "value": "https://sellerapp.com/legal/ondc:fis14/consumer_tnc.html"
                    }
                  ]
                },
                {
                  "display": "true",
                  "descriptor": {
                    "name": "Plan Identifiers",
                    "code": "PLAN_IDENTIFIERS"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "name": "ISIN",
                        "code": "ISIN"
                      },
                      "value": "IN123214324"
                    },
                    {
                      "descriptor": {
                        "name": "RTA Identifier",
                        "code": "RTA_IDENTIFIER"
                      },
                      "value": "02BZ"
                    },
                    {
                      "descriptor": {
                        "name": "AMFI Identifier",
                        "code": "AMFI_IDENTIFIER"
                      },
                      "value": "125487"
                    }
                  ]
                },
                {
                  "display": "true",
                  "descriptor": {
                    "name": "Plan Options",
                    "code": "PLAN_OPTIONS"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "name": "Plan",
                        "code": "PLAN"
                      },
                      "value": "REGULAR"
                    },
                    {
                      "descriptor": {
                        "name": "Option",
                        "code": "OPTION"
                      },
                      "value": "IDCW"
                    },
                    {
                      "descriptor": {
                        "name": "IDCW Option",
                        "code": "IDCW_OPTION"
                      },
                      "value": "PAYOUT"
                    }
                  ]
                }
              ]
            }
          ],
          "fulfillments": [
            {
              "id": "ff_122",
              "type": "LUMPSUM",
              "tags": [
                {
                  "display": "true",
                  "descriptor": {
                    "name": "Thresholds",
                    "code": "THRESHOLDS"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "name": "Amount Minimum",
                        "code": "AMOUNT_MIN"
                      },
                      "value": "1000"
                    },
                    {
                      "descriptor": {
                        "name": "Amount Maximum",
                        "code": "AMOUNT_MAX"
                      },
                      "value": "10000"
                    },
                    {
                      "descriptor": {
                        "name": "Amount Multiples",
                        "code": "AMOUNT_MULTIPLES"
                      },
                      "value": "1"
                    }
                  ]
                }
              ]
            },
            {
              "id": "ff_123",
              "type": "SIP",
              "tags": [
                {
                  "display": "true",
                  "descriptor": {
                    "name": "Thresholds",
                    "code": "THRESHOLDS"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "name": "Frequency",
                        "code": "FREQUENCY"
                      },
                      "value": "P1M"
                    },
                    {
                      "descriptor": {
                        "name": "Frequency Dates",
                        "code": "FREQUENCY_DATES"
                      },
                      "value": "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28"
                    },
                    {
                      "descriptor": {
                        "name": "Amount Minimum",
                        "code": "AMOUNT_MIN"
                      },
                      "value": "5000"
                    },
                    {
                      "descriptor": {
                        "name": "Amount Maximum",
                        "code": "AMOUNT_MAX"
                      },
                      "value": "50000"
                    },
                    {
                      "descriptor": {
                        "name": "Amount Multiples",
                        "code": "AMOUNT_MULTIPLES"
                      },
                      "value": "1"
                    },
                    {
                      "descriptor": {
                        "name": "Installments Count Minimum",
                        "code": "INSTALMENTS_COUNT_MIN"
                      },
                      "value": "6"
                    },
                    {
                      "descriptor": {
                        "name": "Installments Count Maximum",
                        "code": "INSTALMENTS_COUNT_MAX"
                      },
                      "value": "12"
                    },
                    {
                      "descriptor": {
                        "name": "Cumulative Amount Minimum",
                        "code": "CUMULATIVE_AMOUNT_MIN"
                      },
                      "value": "30000"
                    }
                  ]
                }
              ]
            },
            {
              "id": "ff_124",
              "type": "SIP",
              "tags": [
                {
                  "display": "true",
                  "descriptor": {
                    "name": "Thresholds",
                    "code": "THRESHOLDS"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "name": "Frequency",
                        "code": "FREQUENCY"
                      },
                      "value": "P1D"
                    },
                    {
                      "descriptor": {
                        "name": "Amount Minimum",
                        "code": "AMOUNT_MIN"
                      },
                      "value": "1000"
                    },
                    {
                      "descriptor": {
                        "name": "Amount Maximum",
                        "code": "AMOUNT_MAX"
                      },
                      "value": "10000"
                    },
                    {
                      "descriptor": {
                        "name": "Amount Multiples",
                        "code": "AMOUNT_MULTIPLES"
                      },
                      "value": "1"
                    },
                    {
                      "descriptor": {
                        "name": "Installments Count Minimum",
                        "code": "INSTALMENTS_COUNT_MIN"
                      },
                      "value": "30"
                    },
                    {
                      "descriptor": {
                        "name": "Installments Count Maximum",
                        "code": "INSTALMENTS_COUNT_MAX"
                      },
                      "value": "300"
                    },
                    {
                      "descriptor": {
                        "name": "Cumulative Amount Minimum",
                        "code": "CUMULATIVE_AMOUNT_MIN"
                      },
                      "value": "30000"
                    }
                  ]
                }
              ]
            },
            {
              "id": "ff_789",
              "type": "REDEMPTION",
              "tags": [
                {
                  "display": "true",
                  "descriptor": {
                    "name": "Thresholds",
                    "code": "THRESHOLDS"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "name": "Amount Minimum",
                        "code": "AMOUNT_MIN"
                      },
                      "value": "1000"
                    },
                    {
                      "descriptor": {
                        "name": "Amount Maximum",
                        "code": "AMOUNT_MAX"
                      },
                      "value": "10000"
                    },
                    {
                      "descriptor": {
                        "name": "Amount Multiples",
                        "code": "AMOUNT_MULTIPLES"
                      },
                      "value": "1"
                    },
                    {
                      "descriptor": {
                        "name": "Units Minimum",
                        "code": "UNITS_MIN"
                      },
                      "value": "1"
                    },
                    {
                      "descriptor": {
                        "name": "Units Maximum",
                        "code": "UNITS_MAX"
                      },
                      "value": "500"
                    },
                    {
                      "descriptor": {
                        "name": "Units Multiples",
                        "code": "UNITS_MULTIPLES"
                      },
                      "value": "1"
                    }
                  ]
                }
              ]
            }
          ]
        }
      ],
      "tags": [
        {
          "display": "false",
          "descriptor": {
            "name": "BPP Terms of Engagement",
            "code": "BPP_TERMS"
          },
          "list": [
            {
              "descriptor": {
                "name": "Static Terms (Transaction Level)",
                "code": "STATIC_TERMS"
              },
              "value": "https://sellerapp.com/legal/ondc:fis14/static_terms?v=0.1"
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
