import os
import redis
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Redis URL from environment variable with fallback to cloud URL
REDIS_URL = os.getenv(
    "REDIS_URL", 
    "redis://default:e42nmZPX38xqRqehbna0u4gnMoFUBtWW@redis-15120.c264.ap-south-1-1.ec2.redns.redis-cloud.com:15120"
)

class RedisClient:
    _instance: Optional[redis.Redis] = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        if cls._instance is None:
            try:
                cls._instance = redis.Redis.from_url(
                    REDIS_URL,
                    decode_responses=True,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                cls._instance.ping()  # Test connection
                logger.info("✅ Connected to Redis successfully!")
            except redis.exceptions.ConnectionError as e:
                logger.error(f"❌ Failed to connect to Redis: {e}")
                raise
        return cls._instance

    @classmethod
    def update_status(cls, transaction_id: str, action: str, status: str) -> bool:
        try:
            client = cls.get_client()
            key = f"{action}:{transaction_id}"
            client.hset(key, mapping={
                "status": status,
                "transaction_id": transaction_id
            })
            return True
        except Exception as e:
            logger.error(f"Failed to update status in Redis: {e}")
            return False

    @classmethod
    def get_status(cls, transaction_id: str, action: str) -> Dict[str, Any]:
        try:
            client = cls.get_client()
            key = f"{action}:{transaction_id}"
            status = client.hgetall(key)
            return status or {"status": "waiting"}
        except Exception as e:
            logger.error(f"Failed to get status from Redis: {e}")
            return {"status": "error"}

# Create global instance
redis_instance = RedisClient()