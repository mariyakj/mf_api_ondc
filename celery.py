from celery import Celery
from utils.redis_helper import REDIS_URL

# Configure Celery with Redis as broker and backend
celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"]
)
