import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Configure Redis as the broker and result backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "taskmitram",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.workflow_tasks"]
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Celery Beat Config
    beat_schedule={
        "check-scheduled-workflows": {
            "task": "scheduler_heartbeat",
            "schedule": 10.0, # Check every 10 seconds
        },
    }
)

if __name__ == "__main__":
    celery_app.start()
