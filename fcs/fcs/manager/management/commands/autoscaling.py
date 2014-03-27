import json
import os
import subprocess
from django.core.management.base import BaseCommand
from django.db.models.aggregates import Count
from django.utils.timezone import datetime
import time
from requests.exceptions import ConnectionError
from fcs.manager.models import Task, Crawler, TaskServer
import requests


CURRENT_PATH = os.path.dirname(__file__)
PATH_TO_SERVER = CURRENT_PATH + '/../../../../../server/web_server.py'
PATH_TO_CRAWLER = CURRENT_PATH + '/../../../../../crawler/web_interface.py'

SERVER_SPAWN_TIMEOUT = 10
MAX_CRAWLERS = 4
MIN_CRAWLERS = 1
MAX_CRAWLERS_PER_SERVER = 1     # TODO: use task.priority instead this property

CRAWLER_TIMEOUTS_LIMIT = 4


class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        # TODO: assign ports taking database into account (dont spawn servers/crawlers with same address:port)
        self.server_port = 8800
        self.crawler_port = 8900
        self.changed = True

    def handle(self, *args, **options):
        while True:
            self.stdout.write('\n' + str(datetime.now()))
            for task in Task.objects.all():
                self.stdout.write('%s %s %s %s %s' % (str(task.user), str(task.name), str(task.active), str(task.finished), str(task.expire_date)))
                self.check_server_assignment(task)
            self.balance_load()
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
        self.changed = True

    def spawn_crawler(self):
        if len(Crawler.objects.all()) > MAX_CRAWLERS:
            return
        print os.path.abspath(PATH_TO_CRAWLER)
        print 'Spawn crawler'
        subprocess.Popen(['python', PATH_TO_CRAWLER, str(self.crawler_port), 'http://localhost:8000'])  # TODO: change address
        self.crawler_port += 1
        self.changed = True

    def stop_crawler(self, crawler):
        try:
            requests.post(crawler.address + '/stop')
        except ConnectionError:
            pass
        self.changed = True

    def assign_crawlers_to_servers(self):
        servers = TaskServer.objects.all()
        # TODO: dont change good assignment (when nothing changed), remove prints
        for server in servers:
            crawlers = Crawler.objects.annotate(Count('taskserver'))
            print crawlers
            crawlers = sorted(crawlers, key=lambda crawl: crawl.taskserver__count)
            print crawlers
            crawlers = crawlers[:MAX_CRAWLERS_PER_SERVER]
            print crawlers
            server.crawlers = crawlers
            server.save()
            addresses = [crawler.address for crawler in crawlers]
            try:
                requests.post(server.address + '/crawlers', data=json.dumps({'addresses': addresses}))
            except ConnectionError:
                pass
        self.changed = False

    def balance_load(self):
        task_servers = TaskServer.objects.all()
        crawlers = Crawler.objects.all()

        if len(task_servers) > 0:
            if len(crawlers) < MIN_CRAWLERS:
                self.spawn_crawler()

            for crawler in crawlers:
                if crawler.get_timeouts() >= CRAWLER_TIMEOUTS_LIMIT:
                    self.spawn_crawler()
                    crawler.reset_timeouts()
                    break

            if len(crawlers) > MAX_CRAWLERS:
                try:
                    self.stop_crawler(crawlers[0])
                except IndexError:
                    print 'Strange error. Probably MAX_CRAWLERS is negative.'
        else:
            for crawler in crawlers:
                self.stop_crawler(crawler)

        #if self.changed:
        self.assign_crawlers_to_servers()

    def get_status(self):
        pass

    def set_status(self):
        pass

