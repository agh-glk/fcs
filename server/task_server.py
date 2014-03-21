import json
import threading
import time
import requests
from linkdb import LinkDB, BEST_PRIORITY, WORST_PRIORITY
from contentdb import ContentDB


PACKAGE_SIZE = 1
PACKAGE_TIMEOUT = 10


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

        self.web_server = web_server
        self.manager_address = manager_address
        self.link_db = LinkDB()
        self.content_db = ContentDB()
        self.crawlers = []

        self.task_id = task_id
        self.max_links = 0
        self.crawling_type = 0
        self.query = ''

        self.package_cache = {}
        self.package_id = 0

        self.status = Status.INIT

    def init_linkdb(self, whitelist, blacklist):
        # TODO: query, crawling_types, etc. concurrency?
        self.add_links(whitelist)
        self.feedback(blacklist, WORST_PRIORITY)

    def assign_crawlers(self, addresses):
        # TODO: validate addresses
        self.crawlers = addresses

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
        # TODO: refactor - ask management for task definition and crawlers addresses, send server address
        r = requests.post(self.manager_address + '/autoscale/server/register/',
                                data={'task_id': self.task_id, 'address': self.get_address()})
        print r

        if r.status_code == 412 or r.status_code == 404:
            self.stop()
            return
        data = r.json()
        whitelist = data['whitelist']
        blacklist = data['blacklist']
        self.max_links = int(data['max_links'])
        self.crawling_type = int(data['crawling_type'])
        self.query = data['query']
        self.init_linkdb(whitelist, blacklist)
        if data['active']:
            self._set_status(Status.RUNNING)
        else:
            self._set_status(Status.PAUSED)
        self.assign_crawlers(['http://localhost:8900'])

    def _unregister_from_management(self):
        r = requests.post(self.manager_address + '/autoscale/server/unregister/',
                          data={'task_id': self.task_id})
        print r
        # TODO: send some informations to management
        pass

    def update(self):
        # TODO: handle updates made by user in management GUI
        pass

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
        # TODO: automatically stop server when task is stopped
        while self._get_status() != Status.STOPPING:
            if self._get_status() == Status.RUNNING:
                for crawler in self.crawlers:
                    package = self.get_links_package()
                    if package:
                        try:
                            requests.post(crawler + '/put_links', json.dumps(package))
                        except Exception as e:
                            print e
            self.check_cache()
            time.sleep(5)
        # TODO: allow user collect his data for some time before server shutdown
        self._unregister_from_management()
        self.web_server.stop()

    # TODO: remove
    def links(self):
        return self.link_db.content()

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

    def put_data(self, package_id, url, links, content):
        if package_id in self.package_cache:
            self.clear_cache(package_id)
            self.content_db.add_content(url, links, content)
            self.link_db.add_links(links)