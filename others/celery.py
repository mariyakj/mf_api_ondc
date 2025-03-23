from celery import Celery

# Configure Celery
app = Celery(
    "ondc_tasks",
    broker="redis-15120.c264.ap-south-1-1.ec2.redns.redis-cloud.com:15120",  # Redis as the message broker
    backend="redis-15120.c264.ap-south-1-1.ec2.redns.redis-cloud.com:15120",  # Redis as the result backend
)

# Optional: Add task routing and concurrency settings
app.conf.update(
    task_routes={
        "ondc_tasks.*": {"queue": "ondc_queue"},
    },
    worker_concurrency=1,  # Ensure tasks run sequentially
)