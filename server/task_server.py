import json
import threading
import time
import requests
from rest_framework import status
from linkdb import BerkeleyBTreeLinkDB
from key_policy_module import SimpleKeyPolicyModule
from contentdb import ContentDB
from django.utils.timezone import datetime
import sys
from url_processor import URLProcessor
sys.path.append('../')
from common.content_coder import Base64ContentCoder


URL_PACKAGE_SIZE = 10
URL_PACKAGE_TIMEOUT = 15
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
WAIT_FOR_DOWNLOAD_TIME = 25    # in seconds
DATA_PACKAGE_SIZE = 5


class Status(object):
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
        self.link_db = BerkeleyBTreeLinkDB('link_db', SimpleKeyPolicyModule)
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
        self.processing_crawlers = []

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
        r = requests.post(self.manager_address + '/autoscale/server/register/',
                                data={'task_id': self.task_id, 'address': self.get_address()})
        if r.status_code in [status.HTTP_412_PRECONDITION_FAILED, status.HTTP_404_NOT_FOUND]:
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
        except (KeyError, ValueError) as e:
            print e
            self.stop()

    def _unregister_from_management(self):
        requests.post(self.manager_address + '/autoscale/server/unregister/',
                          data={'task_id': self.task_id})

    def update(self, data):
        if self._get_status() in [Status.STOPPING, Status.STARTING]:
            return
        if data['finished']:
            self.stop()
            return

        self.add_links(data['whitelist'].split(','), BerkeleyBTreeLinkDB.DEFAULT_PRIORITY, 0)  # TODO: parse whitelist?
        # TODO: move this method to task server
        #self.link_db.update_blacklist(data['blacklist'])

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
        try:
            while self._get_status() != Status.STOPPING:
                if self._get_status() == Status.RUNNING:
                    for crawler in self.get_idle_crawlers():
                        package = self.get_links_package(crawler)
                        if package:
                            try:
                                requests.post(crawler + '/put_links', json.dumps(package))
                            except Exception as e:
                                self.ban_crawler(crawler)
                                print e
                self.check_cache()
                self.check_limits()
                time.sleep(5)

            shutdown_time = time.time()
            while (time.time() - shutdown_time) < WAIT_FOR_DOWNLOAD_TIME and self.content_db.size() > 0:
                time.sleep(30)
        finally:
            self._unregister_from_management()
            self.web_server.stop()

    def get_idle_crawlers(self):
        self.data_lock.acquire()
        crawlers = self.crawlers
        self.data_lock.release()
        self.cache_lock.acquire()
        processing = self.processing_crawlers
        self.cache_lock.release()
        return [crawler for crawler in crawlers if crawler not in processing]

    def check_limits(self):
        self.data_lock.acquire()
        expire_date = self.expire_date
        max_links = self.max_links
        self.data_lock.release()
        # TODO: change following comparison - size() depends if user downloaded some data
        if (datetime.now() > expire_date) or (self.content_db.size() > max_links):
            self.stop_task()

    def stop_task(self):
        requests.post(self.manager_address + '/autoscale/server/stop_task/',
                          data={'task_id': self.task_id})

    def cache(self, package_id, crawler, links):
        self.cache_lock.acquire()
        self.package_cache[package_id] = (time.time(), links, crawler)
        self.processing_crawlers.append(crawler)
        self.cache_lock.release()

    def get_links_package(self, crawler):
        _links = []
        for i in range(URL_PACKAGE_SIZE):
            _links.append(self.link_db.get_link())
        _links = [link for link in _links if link]
        if _links:
            address = self.get_address()
            crawl_type = self.crawling_type
            package_id = self.package_id
            package = {'server_address': address, 'crawling_type': crawl_type, 'id': package_id, 'links': _links}
            self.cache(package_id, crawler, _links)
            self.package_id += 1
            return package
        else:
            return None

    def check_cache(self):
        cur_time = time.time()
        self.cache_lock.acquire()
        for package_id in self.package_cache.keys():
            if cur_time - self.package_cache[package_id][0] > URL_PACKAGE_TIMEOUT:
                self.readd_links(self.package_cache[package_id][1])
                self.warn_crawler(self.package_cache[package_id][2])
                self.clear_cache(package_id)
        self.cache_lock.release()

    def clear_cache(self, package_id):
        self.cache_lock.acquire()
        try:
            self.processing_crawlers.remove(self.package_cache[package_id][2])
            del self.package_cache[package_id]
        except KeyError:
            pass
        self.cache_lock.release()

    def warn_crawler(self, crawler):
        r = requests.post(self.manager_address + '/autoscale/server/warn_crawler/',
                          data={'address': crawler})
        print r
        # TODO: handle errors if occur

    def ban_crawler(self, crawler):
        r = requests.post(self.manager_address + '/autoscale/server/ban_crawler/',
                          data={'address': crawler})
        print r
        # TODO: handle errors if occur

    def contents(self):
        return self.content_db.content()

    def feedback(self, regex, rate):
        # TODO: change this method to feedback regex (which will be created soon)
        #self.link_db.change_link_priority(regex, rate)
        pass

    def add_links(self, links, priority, depth, domain=None):
        _counter = 0
        for link in links:
            _link = URLProcessor.process(link, domain=domain)
            if not self.link_db.is_in_base(_link):
                print "Added:%s" % _link
                self.link_db.add_link(_link, priority, depth)
                _counter += 1
        print "%d new links added into DB." % _counter

    def readd_links(self, links):
        for link in links:
            self.link_db.change_link_priority(link, BerkeleyBTreeLinkDB.BEST_PRIORITY)

    def _decode_content(self, content):
        return Base64ContentCoder.decode(content)

    def put_data(self, package_id, data):
        if package_id in self.package_cache:
            self.clear_cache(package_id)
            for entry in data:
                self.content_db.add_content(entry['url'], entry['links'], self._decode_content(entry['content']))
                print entry['url']
                self.add_links(entry['links'], BerkeleyBTreeLinkDB.DEFAULT_PRIORITY, 0, domain=entry['url'])

    def _clear(self):
        self.link_db.clear()

    def get_data(self, size=DATA_PACKAGE_SIZE):
        return self.content_db.get_data_package(size)