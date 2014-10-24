import json
import os
import subprocess
from django.core.management.base import BaseCommand
from django.db.models.aggregates import Sum
from django.utils.timezone import datetime
import time
from fcs.manager.models import Task, Crawler, TaskServer, User
import sys
import signal


CURRENT_PATH = os.path.dirname(__file__)
PATH_TO_SERVER = CURRENT_PATH + '/../../../../../server/web_interface.py'
PATH_TO_CRAWLER = CURRENT_PATH + '/../../../../../crawler/web_interface.py'

SERVER_SPAWN_TIMEOUT = 30

MAX_CRAWLERS_NUM = 10
DEFAULT_LINK_QUEUE_SIZE = 20
MIN_LINK_PACKAGE_SIZE = 3

STATS_PERIOD = 120
MIN_CRAWLER_STATS_PERIOD = 60
MIN_SERVER_STATS_PERIOD = 30
AUTOSCALING_PERIOD = 30
LOOP_PERIOD = 10

EFFICIENCY_THRESHOLD = 0.9
LOWER_LOAD_THRESHOLD = 0.4
UPPER_LOAD_THRESHOLD = 0.7

INIT_SERVER_PORT = 18000
INIT_CRAWLER_PORT = 19000


def sigint_signal_handler(num, stack):
    for crawler in Crawler.objects.all():
        crawler.kill()
    for task_server in TaskServer.objects.all():
        task_server.kill()
    time.sleep(10)
    sys.exit(0)


class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.address = '127.0.0.1'  # TODO - ENVIRONMENT DEPENDANT: change management address
        signal.signal(signal.SIGINT, sigint_signal_handler)
        #TODO - FUTURE WORKS: add some function for server/crawler address creation;
        # now it can be bugged with large numbers of servers/crawlers
        self.server_port = max([int(server.address.split(':')[2]) for server in TaskServer.objects.all()]
                               + [INIT_SERVER_PORT]) + 1
        self.crawler_port = max([int(crawler.address.split(':')[2]) for crawler in Crawler.objects.all()]
                                + [INIT_CRAWLER_PORT]) + 1

        self.last_scaling = time.time()
        self.old_crawlers = [crawler.address for crawler in Crawler.objects.all()]
        self.changed = False

    def handle(self, *args, **options):
        if len(args) > 0:
            self.address = args[0]
        while True:
            self.stdout.write('\n' + str(datetime.now()))
            self.print_tasks()
            self.check_tasks_state()
            self.handle_priority_changes()
            self.autoscale()
            self.assign_crawlers_to_servers()
            time.sleep(LOOP_PERIOD)

    def print_tasks(self):
        self.stdout.write('Task list:')
        for task in Task.objects.all():
            self.stdout.write('%s %s %s %s %s %s' % (str(task.user), str(task.name), str(task.active),
                    str(task.finished), str(task.expire_date), 'changed' if task.autoscale_change else ''))
        self.stdout.write('')

    def check_tasks_state(self):
        for task in Task.objects.all():
            self.check_server_assignment(task)

    # TODO - FUTURE WORKS: change server spawn timeout (auto-adjusting)
    def check_server_assignment(self, task):
        if task.is_waiting_for_server():
            if task.last_server_spawn is None or \
                            (datetime.now() - task.last_server_spawn).seconds > SERVER_SPAWN_TIMEOUT:
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
                        task.server.send('/speed', 'post', json.dumps({'urls_per_min': speed}))
                        task.server.urls_per_min = speed
                        task.server.save()
                    else:
                        task.server.send('/speed', 'post', json.dumps({'urls_per_min': 0}))
                        task.server.urls_per_min = 0
                        task.server.save()

    def spawn_task_server(self, task):
        print 'Spawn server for task: ', task
        #TODO - ENVIRONMENT DEPENDANT: change task server spawning
        subprocess.Popen(['python', PATH_TO_SERVER, str(self.server_port), str(task.id), 'http://'+self.address+':8000',
                          self.address])
        task.last_server_spawn = datetime.now()
        task.save()
        self.server_port += 1

    def spawn_crawler(self):
        if len(Crawler.objects.all()) >= MAX_CRAWLERS_NUM:
            return
        print 'Spawn crawler'
        subprocess.Popen(['python', PATH_TO_CRAWLER, str(self.crawler_port), 'http://' + self.address + ':8000'])
        # TODO - ENVIRONMENT DEPENDANT: change crawler spawning
        self.crawler_port += 1

    def assign_crawlers_to_servers(self):
        actual_crawlers = [crawler.address for crawler in Crawler.objects.all()]

        if self.changed or self.old_crawlers != actual_crawlers:
            print '\nAssigning crawlers'
            self.changed = False
            self.old_crawlers = actual_crawlers
            servers = TaskServer.objects.all()
            total_speed = sum([server.urls_per_min for server in servers])
            total_power = len(actual_crawlers) * DEFAULT_LINK_QUEUE_SIZE
            if total_power == 0:
                for server in servers:
                    server.send('/crawlers', 'post', json.dumps({'crawlers': {}}))
                return

            speed_factor = 1. * total_speed / total_power
            crawlers_load = [[address, 0] for address in actual_crawlers]
            length = len(crawlers_load)

            for server in servers:
                if server.urls_per_min == 0:
                    server.send('/crawlers', 'post', json.dumps({'crawlers': {}}))
                else:
                    assignment = {}
                    link_pool = max(1, int(server.urls_per_min / speed_factor))
                    crawlers_num = min(len(actual_crawlers), max(1, link_pool / MIN_LINK_PACKAGE_SIZE))
                    print 'Server', server.address, 'stats:'
                    print '\tspeed:', server.urls_per_min
                    print '\tlink pool:', link_pool
                    print '\tcrawlers:', crawlers_num
                    crawlers_load.sort(key=lambda x: x[1], reverse=True)
                    for i in range(crawlers_num, 0, -1):
                        entry = crawlers_load[length - i]
                        links = min(link_pool / i, max(DEFAULT_LINK_QUEUE_SIZE - entry[1], MIN_LINK_PACKAGE_SIZE))
                        if i == 1:
                            links = link_pool
                        link_pool -= links
                        entry[1] += links
                        assignment[entry[0]] = links
                    server.send('/crawlers', 'post', json.dumps({'crawlers': assignment}))
            print ''

    def autoscale(self):
        task_servers = TaskServer.objects.all()
        crawlers = Crawler.objects.all()
        for crawler in crawlers:
            if not crawler.is_alive():
                crawler.kill()
        for server in task_servers:
            if not server.is_alive():
                server.kill()

        if time.time() - self.last_scaling < AUTOSCALING_PERIOD:
            return

        print '\nAutoscaling'
        task_servers = TaskServer.objects.all()
        crawlers = Crawler.objects.all()

        expected_efficiency = 0
        actual_efficiency = 0
        for server in task_servers:
            response = server.send('/stats', 'post', data=json.dumps({'seconds': STATS_PERIOD}))
            if response:
                data = response.json()
                if data['seconds'] > MIN_SERVER_STATS_PERIOD:
                    expected_efficiency += data['urls_per_min']
                    actual_efficiency += (60. * data['links'] / data['seconds'])

        expected_load = 0
        actual_load = 0
        for crawler in crawlers:
            response = crawler.send('/stats', 'post', data=json.dumps({'seconds': STATS_PERIOD}))
            if response:
                data = response.json()
                if data['seconds'] > MIN_CRAWLER_STATS_PERIOD:
                    expected_load += data['seconds']
                    actual_load += data['load']

        print 'Expected efficiency:', expected_efficiency
        print 'Actual efficiency:', actual_efficiency
        print 'Efficiency percentage:', (1. * actual_efficiency / expected_efficiency) if expected_efficiency else 0.0
        print 'Crawlers up time:', expected_load
        print 'Crawlers load time:', actual_load
        print 'Load percentage: %s \n' % ((1. * actual_load / expected_load) if expected_load else 0.0)

        if actual_efficiency < EFFICIENCY_THRESHOLD * expected_efficiency:
            if len(crawlers) == 0 or actual_load > UPPER_LOAD_THRESHOLD * expected_load:
                self.spawn_crawler()
                self.last_scaling = time.time()
        if actual_load < LOWER_LOAD_THRESHOLD * expected_load:
            crawlers[0].stop()
            self.last_scaling = time.time()
