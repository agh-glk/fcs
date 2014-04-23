import json
import os
import subprocess
from django.core.management.base import BaseCommand
from django.db.models.aggregates import Count, Sum
from django.forms.models import model_to_dict
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
MAX_CRAWLER_LINK_QUEUE = 20
MIN_LINK_PACKAGE_SIZE = 3
INIT_SERVER_PORT = 18000
INIT_CRAWLER_PORT = 19000

CRAWLER_TIMEOUTS_LIMIT = 4


class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.server_port = max([int(server.address.split(':')[2]) for server in TaskServer.objects.all()] + [INIT_SERVER_PORT]) + 1
        self.crawler_port = max([int(crawler.address.split(':')[2]) for crawler in Crawler.objects.all()] + [INIT_CRAWLER_PORT]) + 1

        self.expected_crawlers = len(Crawler.objects.all())
        self.old_crawlers = [crawler.address for crawler in Crawler.objects.all()]
        self.changed = False

    def handle(self, *args, **options):
        while True:
            self.stdout.write('\n' + str(datetime.now()))
            self.print_tasks()
            self.check_tasks_state()
            self.handle_priority_changes()
            self.assign_crawlers_to_servers()
            self.autoscale()
            time.sleep(10)

    def print_tasks(self):
        for task in Task.objects.all():
            self.stdout.write('%s %s %s %s %s %s' % (str(task.user), str(task.name), str(task.active),
                    str(task.finished), str(task.expire_date), 'changed' if task.autoscale_change else ''))

    def check_tasks_state(self):
        for task in Task.objects.all():
            self.check_server_assignment(task)

    # TODO: change management address, crawler spawn timeout?
    def check_server_assignment(self, task):
        if task.is_waiting_for_server():
            if task.last_server_spawn is None:
                self.spawn_task_server(task)
            elif (datetime.now() - task.last_server_spawn).seconds > SERVER_SPAWN_TIMEOUT:
                self.spawn_task_server(task)

    def handle_priority_changes(self):
        for user in User.objects.filter(quota__isnull=False):
            urls_per_min = user.quota.urls_per_min
            reassign_speed = False
            for task in user.task_set.all():
                if task.autoscale_change:
                    reassign_speed = True
                    task.autoscale_change = False
                    task.save()
            if reassign_speed:
                self.changed = True
                active_tasks = user.task_set.filter(active=True, server__isnull=False)
                priority_sum = active_tasks.aggregate(Sum('priority'))['priority__sum']
                for task in user.task_set.filter(server__isnull=False):
                    if task.active:
                        speed = urls_per_min * task.priority / priority_sum
                        task.server.send('/speed', 'post', json.dumps({'speed': speed}))
                        task.server.urls_per_min = speed
                        task.server.save()
                    else:
                        task.server.send('/speed', 'post', json.dumps({'speed': 0}))
                        task.server.urls_per_min = 0
                        task.server.save()

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
        actual_crawlers = [crawler.address for crawler in Crawler.objects.all()]

        if self.changed or self.old_crawlers != actual_crawlers:
            self.changed = False
            self.old_crawlers = actual_crawlers
            servers = TaskServer.objects.all()
            total_speed = sum([server.urls_per_min for server in servers])
            total_power = len(actual_crawlers) * MAX_CRAWLER_LINK_QUEUE
            if total_power == 0:
                for server in servers:
                    server.send('/crawlers', 'post', json.dumps({}))
                return

            speed_factor = total_speed / total_power

            crawlers_load = [[address, 0] for address in actual_crawlers]
            length = len(crawlers_load)

            for server in servers:
                if server.speed == 0:
                    server.send('/crawlers', 'post', json.dumps({}))
                else:
                    assignment = {}
                    link_pool = max(1, server.speed / speed_factor)
                    crawlers_num = min(len(actual_crawlers), max(1, link_pool / MIN_LINK_PACKAGE_SIZE))
                    crawlers_load.sort(key=lambda x: x[1], reverse=True)
                    for i in range(crawlers_num, 0, -1):
                        entry = crawlers_load[length - i]
                        links = max(0, min(link_pool / i, MAX_CRAWLER_LINK_QUEUE - entry[1]))
                        if i == 1:
                            links = link_pool
                        link_pool -= links
                        entry[1] += links
                        assignment[entry[0]] = links
                    server.send('/crawlers', 'post', json.dumps(assignment))
        #TODO: in autoscale method check stats and spawn/stop crawler
        #TODO: remove crawler warnings

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


