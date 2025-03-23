from celery import Celery as CeleryApp
from redis_client import REDIS_URL

# Configure Celery to use Redis as both broker and backend
celery_app = CeleryApp(
    'ondc_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Celery Configuration
celery_app.conf.update(
    # Broker settings
    broker_url=REDIS_URL,
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=None,
    broker_transport_options={'visibility_timeout': 3600},

    # Result backend settings
    result_backend=REDIS_URL,
    
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Time settings
    timezone='UTC',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    
    # Task settings
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60  # 25 minutes
)

if __name__ == '__main__':
    print(f"Broker URL: {celery_app.conf.broker_url}")
    print(f"Result Backend: {celery_app.conf.result_backend}")