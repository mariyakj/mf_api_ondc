from celery import Celery
from config import Config  # Import the correct config class

celery = Celery(
    "tasks",
    broker=Config.REDIS_URL,  # Use Redis as the broker
    backend=Config.REDIS_URL  # Use Redis as the result backend
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_expires=3600,
)
