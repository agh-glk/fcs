from celery import Celery
from django.conf import settings

app = Celery('fcs.manager.celery_tasks', broker='amqp://guest:guest@localhost:5672//')
settings.configure()

@app.task
def add(x, y):
    return x + y

add.delay(4, 4)