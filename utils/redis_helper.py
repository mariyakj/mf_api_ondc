import redis
from config import config  # Import the config object

# Initialize Redis client
redis_client = redis.Redis.from_url(config.REDIS_URL, decode_responses=True)

def test_redis():
    """Function to test Redis connection"""
    try:
        redis_client.ping()
        print("✅ Connected to Redis successfully!")
    except redis.exceptions.ConnectionError:
        print("❌ Failed to connect to Redis.")

# Uncomment to test connection when script runs
# test_redis()
