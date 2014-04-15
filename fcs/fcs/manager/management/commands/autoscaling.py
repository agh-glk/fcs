import json
import os
import subprocess
from django.core.management.base import BaseCommand
from django.db.models.aggregates import Count, Sum
from django.utils.timezone import datetime
import time
from requests.exceptions import ConnectionError
from fcs.manager.models import Task, Crawler, TaskServer, User
import requests


CURRENT_PATH = os.path.dirname(__file__)
PATH_TO_SERVER = CURRENT_PATH + '/../../../../../server/web_interface.py'
PATH_TO_CRAWLER = CURRENT_PATH + '/../../../../../crawler/web_interface.py'

SERVER_SPAWN_TIMEOUT = 10
MAX_CRAWLERS = 10    # recommended value: greater than 10 (because priority max value can be 10)
MAX_ASSIGNMENT_DIFFERENCE = 1
INIT_SERVER_PORT = 18000
INIT_CRAWLER_PORT = 19000

CRAWLER_TIMEOUTS_LIMIT = 4


class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.server_port = max([int(server.address.split(':')[2]) for server in TaskServer.objects.all()] + [INIT_SERVER_PORT]) + 1
        self.crawler_port = max([int(crawler.address.split(':')[2]) for crawler in Crawler.objects.all()] + [INIT_CRAWLER_PORT]) + 1

    def handle(self, *args, **options):
        while True:
            self.stdout.write('\n' + str(datetime.now()))
            self.print_tasks()
            self.check_tasks_state()
            self.handle_priority_changes()
            self.autoscale()
            time.sleep(10)

    def print_tasks(self):
        for task in Task.objects.all():
            self.stdout.write('%s %s %s %s %s %s' % (str(task.user), str(task.name), str(task.active),
                    str(task.finished), str(task.expire_date), 'changed' if task.autoscale_change else ''))

    def check_tasks_state(self):
        for task in Task.objects.all():
            self.check_server_assignment(task)

    def handle_priority_changes(self):
        for user in User.objects.all():
            urls_per_min = user.quota.urls_per_min
            reassign = False
            for task in user.task_set:
                if task.autoscale_change:
                    reassign = True
                    task.autoscale_change = False
                    task.save()
            if reassign:
                active_tasks = user.task_set.filter(active=True).exclude(server=None)
                priority_sum = active_tasks.aggregate(Sum('priority'))['priority__sum']
                for task in user.task_set: #tasks with server
                    pass
                    # TODO: make server url_per_min=0 if not active


    # TODO: change management address, keep alive crawlers and servers, crawler spawn timeout?
    # TODO: improve shutdowns of server and crawlers when exception occurs
    def check_server_assignment(self, task):
        if task.is_waiting_for_server():
            if task.last_server_spawn is None:
                self.spawn_task_server(task)
            elif (datetime.now() - task.last_server_spawn).seconds > SERVER_SPAWN_TIMEOUT:
                self.spawn_task_server(task)

    def spawn_task_server(self, task):
        print os.path.abspath(PATH_TO_SERVER)
        print 'Spawn server for task: ', task
        subprocess.Popen(['python', PATH_TO_SERVER, str(self.server_port), str(task.id), 'http://localhost:8000'])
        # TODO: change management address
        task.last_server_spawn = datetime.now()
        task.save()
        self.server_port += 1

    def spawn_crawler(self):
        if len(Crawler.objects.all()) >= MAX_CRAWLERS:
            return
        print os.path.abspath(PATH_TO_CRAWLER)
        print 'Spawn crawler'
        subprocess.Popen(['python', PATH_TO_CRAWLER, str(self.crawler_port), 'http://localhost:8000'])
        # TODO: change management address
        self.crawler_port += 1

    def assign_crawlers_to_servers(self):
        servers = TaskServer.objects.all()
        for server in servers:
            crawlers = []
            if server.task.active:
                crawlers = Crawler.objects.annotate(Count('taskserver'))
                crawlers = sorted(crawlers, key=lambda crawl: crawl.taskserver__count)
                print crawlers
                crawlers = crawlers[:server.task.priority]
            server.crawlers = crawlers
            server.save()
            addresses = [crawler.address for crawler in crawlers]
            try:
                requests.post(server.address + '/crawlers', data=json.dumps({'addresses': addresses}))
            except ConnectionError:
                server.delete()

    def autoscale(self):
        # TODO: in future - get and check crawler load time and adjust assignment
        task_servers = TaskServer.objects.all()
        crawlers = Crawler.objects.annotate(Count('taskserver'))

        # TODO: don't reassign if there are less crawlers than server's priority
        reassign = False
        for server in task_servers:
            if (not server.task.active) and (len(server.crawlers.all()) > 0):
                reassign = True
                break
            elif server.task.active and len(server.crawlers.all()) != server.task.priority:
                reassign = True
                break

        sorted_crawl = sorted(crawlers, key=lambda crawl: crawl.taskserver__count)
        if len(sorted_crawl) > 1 and (sorted_crawl[-1].taskserver__count - sorted_crawl[0].taskserver__count) > MAX_ASSIGNMENT_DIFFERENCE:
            reassign = True

        if reassign:
            self.assign_crawlers_to_servers()

        # TODO: do it... smarter
        task_servers = TaskServer.objects.all()
        crawlers = Crawler.objects.annotate(Count('taskserver'))
        if len(task_servers) > 0:
            min_crawlers = max([server.task.priority for server in task_servers if server.task.active] + [0])
            if len(crawlers) < min_crawlers:
                self.spawn_crawler()

        for crawler in crawlers[MAX_CRAWLERS:]:
            crawler.stop()
        for crawler in crawlers:
            if not crawler.is_alive():
                crawler.kill()
            elif crawler.taskserver__count == 0:
                crawler.stop()
            elif crawler.get_timeouts() >= CRAWLER_TIMEOUTS_LIMIT:
                self.spawn_crawler()
                crawler.reset_timeouts()

        for server in task_servers:
            if not server.is_alive():
                server.kill()


