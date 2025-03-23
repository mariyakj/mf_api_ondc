import os
import redis
from dotenv import load_dotenv  # Load environment variables from .env

# Load environment variables
load_dotenv()

# Get Redis URL from environment variable
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")  

# Initialize Redis client
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def test_redis():
    """Function to test Redis connection"""
    try:
        redis_client.ping()
        print("✅ Connected to Redis successfully!")
    except redis.exceptions.ConnectionError:
        print("❌ Failed to connect to Redis.")

# Uncomment to test connection when script runs
# test_redis()
