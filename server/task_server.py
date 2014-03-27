import json
import threading
import time
import requests
from linkdb import LinkDB, BEST_PRIORITY
from contentdb import ContentDB
from django.utils.timezone import datetime
import sys
sys.path.append('../')
from common.content_coder import Base64ContentCoder


PACKAGE_SIZE = 10
PACKAGE_TIMEOUT = 30
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class Status:
    INIT = 0
    STARTING = 1
    RUNNING = 2
    PAUSED = 3
    STOPPING = 4


class TaskServer(threading.Thread):
    def __init__(self, web_server, task_id, manager_address):
        threading.Thread.__init__(self)
        self.status_lock = threading.Lock()
        self.cache_lock = threading.RLock()
        self.data_lock = threading.RLock()

        self.web_server = web_server
        self.manager_address = manager_address
        self.link_db = LinkDB()
        self.content_db = ContentDB()
        self.crawlers = []

        self.task_id = task_id
        self.max_links = 0
        self.priority = 0
        self.expire_date = None
        self.crawling_type = 0
        self.query = ''

        self.package_cache = {}
        self.package_id = 0

        self.status = Status.INIT

    def assign_crawlers(self, addresses):
        # TODO: validate addresses
        self.data_lock.acquire()
        self.crawlers = addresses
        self.data_lock.release()

    def get_address(self):
        return 'http://' + self.web_server.get_host()

    def _set_status(self, status):
        self.status_lock.acquire()
        self.status = status
        self.status_lock.release()

    def _get_status(self):
        self.status_lock.acquire()
        status = self.status
        self.status_lock.release()
        return status

    def _register_to_management(self):
        # TODO: refactor - status codes, ask management for task definition and crawlers addresses, send server address
        r = requests.post(self.manager_address + '/autoscale/server/register/',
                                data={'task_id': self.task_id, 'address': self.get_address()})
        print r
        if r.status_code == 412 or r.status_code == 404:
            self.stop()
            return

        self._set_status(Status.RUNNING)
        try:
            data = r.json()
            self.update(data)

            self.data_lock.acquire()
            self.crawling_type = int(data['crawling_type'])
            self.query = data['query']
            self.data_lock.release()
            # TODO: remove this line from this function
            #self.assign_crawlers(['http://localhost:8900'])
        except (KeyError, ValueError) as e:
            print e
            self._set_status(Status.STOPPING)

    def _unregister_from_management(self):
        r = requests.post(self.manager_address + '/autoscale/server/unregister/',
                          data={'task_id': self.task_id})
        print r
        # TODO: send some information to management
        pass

    def update(self, data):
        if self._get_status() in [Status.STOPPING, Status.STARTING]:
            return
        if data['finished']:
            self._set_status(Status.STOPPING)
            return

        self.link_db.add_links(data['whitelist'].split(','), BEST_PRIORITY)  # TODO: parse whitelist?
        self.link_db.update_blacklist(data['blacklist'])

        self.data_lock.acquire()
        self.priority = int(data['priority'])
        self.max_links = int(data['max_links'])
        self.expire_date = datetime.strptime(data['expire_date'], DATE_FORMAT)
        self.data_lock.release()

        if data['active']:
            self.resume()
        else:
            self.pause()

    def pause(self):
        if self._get_status() == Status.RUNNING:
            self._set_status(Status.PAUSED)

    def resume(self):
        if self._get_status() == Status.PAUSED:
            self._set_status(Status.RUNNING)

    def stop(self):
        self._set_status(Status.STOPPING)

    def run(self):
        self._set_status(Status.STARTING)
        self.web_server.start()
        self._register_to_management()
        while self._get_status() != Status.STOPPING:
            if self._get_status() == Status.RUNNING:
                for crawler in self.crawlers:
                    package = self.get_links_package()
                    if package:
                        try:
                            # TODO: dont send to crawler which is currently processing request
                            requests.post(crawler + '/put_links', json.dumps(package))
                        except Exception as e:
                            print e
            self.check_cache()
            self.check_limits()
            time.sleep(5)
        # TODO: allow user collect his data for some time before server shutdown
        self._unregister_from_management()
        self.web_server.stop()

    # TODO: remove
    def links(self):
        return self.link_db.content()

    def check_limits(self):
        self.data_lock.acquire()
        expire_date = self.expire_date
        max_links = self.max_links
        self.data_lock.release()
        if (datetime.now() > expire_date) or (self.content_db.size() > max_links):
            self.stop_task()

    def stop_task(self):
        r = requests.post(self.manager_address + '/autoscale/server/stop_task/',
                          data={'task_id': self.task_id})
        print r
        # TODO: handle errors if occur

    def cache(self, package_id, links):
        self.cache_lock.acquire()
        self.package_cache[package_id] = (time.time(), links)
        self.cache_lock.release()

    def get_links_package(self):
        links = self.link_db.get_links(PACKAGE_SIZE)
        if links:
            address = self.get_address()
            crawl_type = self.crawling_type
            package_id = self.package_id
            package = {'server_address': address, 'crawling_type': crawl_type, 'id': package_id, 'links': links}
            self.cache(package_id, links)
            self.package_id += 1
            return package
        else:
            return None

    def check_cache(self):
        cur_time = time.time()
        self.cache_lock.acquire()
        for package_id in self.package_cache.keys():
            if cur_time - self.package_cache[package_id][0] > PACKAGE_TIMEOUT:
                self.readd_links(self.package_cache[package_id][1])
                self.clear_cache(package_id)
        self.cache_lock.release()

    def clear_cache(self, package_id):
        self.cache_lock.acquire()
        try:
            del self.package_cache[package_id]
        except KeyError:
            pass
        self.cache_lock.release()

    def contents(self):
        return self.content_db.content()

    def feedback(self, regex, rate):
        self.link_db.feedback(regex, rate)

    def add_links(self, links):
        self.link_db.add_links(links)

    def readd_links(self, links):
        self.link_db.add_links(links, BEST_PRIORITY, True)

    def _decode_content(self, content):
        return Base64ContentCoder.decode(content)

    def put_data(self, package_id, data):
        if package_id in self.package_cache:
            self.clear_cache(package_id)
            for entry in data:
                self.content_db.add_content(entry['url'], entry['links'], self._decode_content(entry['content']))
                self.link_db.add_links(entry['links'])