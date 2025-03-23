import redis
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

REDIS_URL = "redis://default:e42nmZPX38xqRqehbna0u4gnMoFUBtWW@redis-15120.c264.ap-south-1-1.ec2.redns.redis-cloud.com:15120"

def get_redis_client() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True)

def update_status(transaction_id: str, action: str, status: str) -> bool:
    try:
        client = get_redis_client()
        key = f"{action}:{transaction_id}"
        client.hset(key, mapping={
            "status": status,
            "transaction_id": transaction_id
        })
        return True
    except Exception as e:
        logger.error(f"Redis update failed: {e}")
        return False

def get_status(transaction_id: str, action: str) -> Dict[str, Any]:
    try:
        client = get_redis_client()
        key = f"{action}:{transaction_id}"
        status = client.hgetall(key)
        return status if status else {"status": "waiting"}
    except Exception as e:
        logger.error(f"Redis get failed: {e}")
        return {"status": "error"}