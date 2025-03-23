from celery import Celery
from utils.redis_helper import REDIS_URL
import os

# Create Celery instance with Redis as both broker and backend
celery_app = Celery(
    'ondc_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Force Redis as broker
os.environ.setdefault('CELERY_BROKER_URL', REDIS_URL)

# Celery Configuration
celery_app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_transport_options={'visibility_timeout': 3600},
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
)

# Print configuration when running directly
if __name__ == '__main__':
    print(f"Broker URL: {celery_app.conf.broker_url}")
    print(f"Result Backend: {celery_app.conf.result_backend}")