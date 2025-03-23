import os
from celery import Celery
from redis_client import REDIS_URL

# Configure Celery to use Redis as both broker and backend
celery_app = Celery(
    'ondc_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL,
    broker_connection_retry_on_startup=True
)

# Celery Configuration
celery_app.conf.update(
    broker_connection_retry=True,
    broker_connection_max_retries=None,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)