import time
import base64
import logging
import nacl.signing
from nacl.encoding import Base64Encoder
from nacl.exceptions import BadSignatureError

logger = logging.getLogger(__name__)

CONFIG = {
    "PRIVATE_KEY": "9MyRGumH8I+A6EHDOqz7XcUYsAGxz7NuGO6Pi13FaR+nSJzoeOX6yjTXZc/Uib2oyHe24PADJoYtrw0Fex5kvg==",
    "KEY_ID": "staging.onesmf.com|58072g41-8cae-2f577-b8ca-24273d9b07b3|ed25519",
    "SIGNATURE_VALIDITY": 3600,
}

def sign_message(message: str) -> str:
    """Signs a message using Ed25519 private key."""
    try:
        logger.debug(f"Signing message: {message}")
        
        private_key_bytes = base64.b64decode(CONFIG["PRIVATE_KEY"])
        if len(private_key_bytes) != 64:
            raise ValueError("Invalid private key length")
            
        signing_key = nacl.signing.SigningKey(private_key_bytes[:32])
        signed_bytes = signing_key.sign(message.encode()).signature
        signature = base64.b64encode(signed_bytes).decode()
        
        # Verify signature immediately after creation
        verify_key = signing_key.verify_key
        try:
            verify_key.verify(message.encode(), signed_bytes)
            logger.debug("✅ Signature verified successfully")
        except BadSignatureError:
            logger.error("❌ Signature verification failed")
            raise ValueError("Generated signature failed verification")
            
        return signature
        
    except Exception as e:
        logger.error(f"❌ Signing failed: {str(e)}")
        raise ValueError(f"Signing failed: {str(e)}")

def generate_auth_header(digest_base64: str) -> str:
    """Generates the authentication header."""
    try:
        created = int(time.time())
        expires = created + CONFIG["SIGNATURE_VALIDITY"]

        # Match the exact format from working code
        signing_string = f"(created): {created}\n(expires): {expires}\ndigest: BLAKE-512={digest_base64}"
        logger.debug(f"Generated signing string: {signing_string}")
        
        signature = sign_message(signing_string)
        logger.debug(f"Generated signature: {signature}")

        auth_header = (
            f'Signature keyId="{CONFIG["KEY_ID"]}",'
            f'algorithm="ed25519",'
            f'created="{created}",'
            f'expires="{expires}",'
            f'headers="(created) (expires) digest",'
            f'signature="{signature}"'
        )
        
        logger.debug(f"Generated auth header: {auth_header}")
        return auth_header

    except Exception as e:
        logger.error(f"❌ Auth header generation failed: {str(e)}")
        raise