import os
import subprocess
from django.core.management.base import BaseCommand
from django.utils.timezone import datetime
import time
from fcs.manager.models import Task
import requests


CURRENT_PATH = os.path.dirname(__file__)
PATH_TO_SERVER = CURRENT_PATH + '/../../../../../server/web_server.py'
PATH_TO_CRAWLER = CURRENT_PATH + '/../../../../../crawler/web_interface.py'

SERVER_SPAWN_TIMEOUT = 1


class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.server_port = 8800
        self.crawler_port = 8900

    def handle(self, *args, **options):
        while True:
            self.stdout.write('\n' + str(datetime.now()))
            for task in Task.objects.all():
                self.stdout.write('%s %s %s %s %s' % (str(task.user), str(task.name), str(task.active), str(task.finished), str(task.expire_date)))
                self.check_server_assignment(task)
            time.sleep(10)

    # TODO: task server management, crawler management, add TaskServer and Crawler models, check links number, change management address
    def check_server_assignment(self, task):
        if task.is_waiting_for_server():
            if task.last_server_spawn is None:
                self.spawn_task_server(task)
            elif (datetime.now() - task.last_server_spawn).seconds > SERVER_SPAWN_TIMEOUT:
                self.spawn_task_server(task)

    def spawn_task_server(self, task):
        print os.path.abspath(PATH_TO_SERVER)
        print 'Spawn server for task: ', task
        subprocess.Popen(['python', PATH_TO_SERVER, str(self.server_port), str(task.id), 'http://localhost:8000'])  # TODO: change address
        task.last_server_spawn = datetime.now()
        task.save()
        self.server_port += 1

    def spawn_crawler(self):
        print os.path.abspath(PATH_TO_CRAWLER)
        print 'Spawn crawler'
        subprocess.Popen(['python', PATH_TO_CRAWLER, str(self.crawler_port), 'http://localhost:8000'])  # TODO: change address
        self.crawler_port += 1

    def stop_crawler(self):
        pass

    def assign_crawlers_to_server(self):
        pass

    def balance_load(self):
        pass

    def get_status(self):
        pass

    def set_status(self):
        pass

