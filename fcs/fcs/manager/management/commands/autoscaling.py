from django.core.management.base import BaseCommand
from django.utils.timezone import datetime
import time
from fcs.manager.models import Task


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            self.stdout.write(str(datetime.now()))
            for task in Task.objects.all():
                self.stdout.write('%s %s %s %s %s' % (str(task.user), str(task.name), str(task.active), str(task.finished), str(task.expire_date)))
                check_expire_date(task)
            time.sleep(5)


def check_expire_date(task):
    if task.expire_date < datetime.now():
        task.stop()


# TODO: task server management, crawler management, add TaskServer and Crawler models
def check_task_assignment():
    pass


def spawn_task_server():
    pass


def spawn_crawler():
    pass


def stop_server():
    pass


def pause_server():
    pass


def resume_server():
    pass


def stop_crawler():
    pass


def assign_crawlers_to_server():
    pass


def balance_load():
    pass


def get_status():
    pass


def set_status():
    pass

