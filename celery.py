from celery import Celery
from config import config  # Import config

celery = Celery("tasks", broker=config.REDIS_URL)

celery.conf.update(
    result_backend=config.REDIS_URL,
    task_serializer="json",
)

@celery.task
def test_task():
    return "Celery is working with Redis!"
