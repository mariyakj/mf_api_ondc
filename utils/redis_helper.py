import redis

REDIS_URL = "redis://default:e42nmZPX38xqRqehbna0u4gnMoFUBtWW@redis-15120.c264.ap-south-1-1.ec2.redns.redis-cloud.com:15120"

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def test_redis():
    """Function to test Redis connection"""
    try:
        redis_client.ping()
        print("✅ Connected to Redis successfully!")
    except redis.exceptions.ConnectionError:
        print("❌ Failed to connect to Redis.")

# Uncomment this to test connection when script runs
# test_redis()
