import time
import base64
from blake3 import blake3
from nacl.signing import SigningKey
from nacl.encoding import Base64Encoder

CONFIG = {
    "PRIVATE_KEY": "9MyRGumH8I+A6EHDOqz7XcUYsAGxz7NuGO6Pi13FaR+nSJzoeOX6yjTXZc/Uib2oyHe24PADJoYtrw0Fex5kvg==",
    "KEY_ID": "staging.onesmf.com|58072g41-8cae-2f577-b8ca-24273d9b07b3|ed25519",
    "SIGNATURE_VALIDITY": 3600,  # 1 hour in seconds
}

def sign_message(message: str) -> str:
    """Signs a message using Ed25519 private key."""
    private_key_bytes = base64.b64decode(CONFIG["PRIVATE_KEY"])
    signing_key = SigningKey(private_key_bytes[:32])  # Secret part of the key
    signature = signing_key.sign(message.encode(), encoder=Base64Encoder).signature
    return signature.decode()

def generate_auth_header(hashed_body: str) -> str:
    """Generates the authentication header with corrected timestamp and encoding."""
    created = int(time.time())  # Corrected timestamp
    expires = created + CONFIG["SIGNATURE_VALIDITY"]

    signing_string = f"(created): {created}\n(expires): {expires}\ndigest: BLAKE-512={hashed_body}"
    signature = sign_message(signing_string)

    return (
        f'Signature keyId="{CONFIG["KEY_ID"]}",algorithm="ed25519",'
        f'created="{created}",expires="{expires}",headers="(created) (expires) digest",'
        f'signature="{signature}"'
    )
