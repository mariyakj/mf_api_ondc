import redis
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis Configuration
REDIS_URL = "redis://default:e42nmZPX38xqRqehbna0u4gnMoFUBtWW@redis-15120.c264.ap-south-1-1.ec2.redns.redis-cloud.com:15120"

class RedisClient:
    _instance: Optional[redis.Redis] = None
    
    @classmethod
    def get_instance(cls) -> redis.Redis:
        if cls._instance is None:
            cls._instance = redis.from_url(REDIS_URL, decode_responses=True)
        return cls._instance

    @classmethod
    def update_status(cls, transaction_id: str, action: str, status: str) -> bool:
        try:
            redis_client = cls.get_instance()
            key = f"{action}:{transaction_id}"
            redis_client.hset(key, mapping={
                "status": status,
                "transaction_id": transaction_id
            })
            return True
        except Exception as e:
            logger.error(f"Redis update failed: {e}")
            return False

    @classmethod
    def get_status(cls, transaction_id: str, action: str) -> Dict[str, Any]:
        try:
            redis_client = cls.get_instance()
            key = f"{action}:{transaction_id}"
            status = redis_client.hgetall(key)
            return status if status else {"status": "waiting"}
        except Exception as e:
            logger.error(f"Redis get failed: {e}")
            return {"status": "error"}

# Create singleton instance
redis_client = RedisClient()