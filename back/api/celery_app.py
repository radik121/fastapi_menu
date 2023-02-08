from celery import Celery
from config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_PORT, RABBITMQ_USER

celery_app = Celery(
    "create_file_xlsx",
    broker=f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//",
    backend="rpc://",
    include=["api.tasks"],
)

if __name__ == "__main__":
    celery_app.start()
