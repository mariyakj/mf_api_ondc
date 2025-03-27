import time
import base64
import nacl.signing
from nacl.encoding import Base64Encoder

CONFIG = {
    "PRIVATE_KEY": "9MyRGumH8I+A6EHDOqz7XcUYsAGxz7NuGO6Pi13FaR+nSJzoeOX6yjTXZc/Uib2oyHe24PADJoYtrw0Fex5kvg==",
    "KEY_ID": "staging.onesmf.com|58072g41-8cae-2f577-b8ca-24273d9b07b3|ed25519",
    "SIGNATURE_VALIDITY": 3600,
}

def sign_message(message: str) -> str:
    """Signs a message using Ed25519 private key."""
    try:
        private_key_bytes = base64.b64decode(CONFIG["PRIVATE_KEY"])
        if len(private_key_bytes) != 64:
            raise ValueError("Invalid private key length")
            
        signing_key = nacl.signing.SigningKey(private_key_bytes[:32])
        signed_bytes = signing_key.sign(message.encode()).signature
        return base64.b64encode(signed_bytes).decode()
        
    except Exception as e:
        raise ValueError(f"Signing failed: {str(e)}")

def generate_auth_header(digest_base64: str) -> str:
    """Generates the authentication header."""
    created = int(time.time())
    expires = created + CONFIG["SIGNATURE_VALIDITY"]

    # Match the exact format from working code
    signing_string = f"(created): {created}\n(expires): {expires}\ndigest: BLAKE-512={digest_base64}"
    signature = sign_message(signing_string)

    return (
        f'Signature keyId="{CONFIG["KEY_ID"]}",'
        f'algorithm="ed25519",'
        f'created="{created}",'
        f'expires="{expires}",'
        f'headers="(created) (expires) digest",'
        f'signature="{signature}"'
    )