import redis
import os

# Get Redis URL from environment variables
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

try:
    client = redis.from_url(redis_url)
    response = client.ping()
    print("✅ Redis is working!" if response else "❌ Redis ping failed!")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
