import json
import logging
import re
import threading
import time
import sys

import requests
from requests.exceptions import ConnectionError
from rest_framework import status
from linkdb import BerkeleyBTreeLinkDB
from key_policy_module import SimpleKeyPolicyModule
from contentdb import BerkeleyContentDB
from django.utils.timezone import datetime
import sys
from url_processor import URLProcessor
from crawling_depth_policy import SimpleCrawlingDepthPolicy, RealDepthCrawlingDepthPolicy

sys.path.append('../')
from common.content_coder import Base64ContentCoder


URL_PACKAGE_SIZE = 8
URL_PACKAGE_TIMEOUT = 30
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
WAIT_FOR_DOWNLOAD_TIME = 25    # in seconds
DATA_PACKAGE_SIZE = 5


class Status(object):
    INIT = 0
    STARTING = 1
    RUNNING = 2
    PAUSED = 3
    STOPPING = 4
    KILLED = 5


class TaskServer(threading.Thread):
    def __init__(self, web_server, task_id, manager_address, max_url_depth=1):
        threading.Thread.__init__(self)
        self.status_lock = threading.Lock()
        self.cache_lock = threading.RLock()
        self.data_lock = threading.RLock()

        self.web_server = web_server
        self.manager_address = manager_address
        self.link_db = BerkeleyBTreeLinkDB('link_db', SimpleKeyPolicyModule)
        self.content_db = BerkeleyContentDB('content_db')

        self.crawlers = []
        self.task_id = task_id
        self.max_links = 0
        self.priority = 0
        self.expire_date = None
        self.mime_type = []
        self.uuid = ''
        self.whitelist = []
        self.blacklist = []

        self.package_cache = {}
        self.package_id = 0
        self.processing_crawlers = []
        self.max_url_depth = max_url_depth
        self.status = Status.INIT

        self.logger = logging.getLogger('server')
        _file_handler = logging.FileHandler('server%s.log' % task_id)
        _formatter = logging.Formatter('<%(asctime)s>:%(levelname)s: %(message)s')
        _file_handler.setFormatter(_formatter)
        self.logger.addHandler(_file_handler)
        self.logger.setLevel(logging.DEBUG)

    def assign_crawlers(self, addresses):
        # TODO: validate addresses
        self.data_lock.acquire()
        self.crawlers = addresses
        self.data_lock.release()
        self.logger.debug('%d crawlers assigned' % len(addresses))

    def get_address(self):
        return 'http://' + self.web_server.get_host()

    def _set_status(self, status):
        self.status_lock.acquire()
        self.status = status
        self.status_lock.release()
        self.logger.debug('Changed status to: %d' % status)

    def _get_status(self):
        self.status_lock.acquire()
        status = self.status
        self.status_lock.release()
        return status

    def _register_to_management(self):
        r = requests.post(self.manager_address + '/autoscale/server/register/',
                                data={'task_id': self.task_id, 'address': self.get_address()})
        self.logger.debug('Registering to management. Return code: %d' % r.status_code)
        if r.status_code in [status.HTTP_412_PRECONDITION_FAILED, status.HTTP_404_NOT_FOUND]:
            self.stop()
            return

        self._set_status(Status.RUNNING)
        try:
            data = r.json()
            self.update(data)
            self.add_links(data['start_links'], self.link_db.DEFAULT_PRIORITY, 0)
            self.data_lock.acquire()
            self.uuid = data['uuid']
            self.data_lock.release()
            self.logger.debug('Registered to management')
        except (KeyError, ValueError) as e:
            self.logger.debug('Error while registering: %s' % str(e))
            self.stop()

    def _unregister_from_management(self):
        r = requests.post(self.manager_address + '/autoscale/server/unregister/',
                          data={'task_id': self.task_id, 'uuid': self.uuid})
        self.logger.debug('Unregistering from management. Return code: %d' % r.status_code)

    def update(self, data):
        self.logger.debug('Updating task server')
        if self._get_status() in [Status.STOPPING, Status.STARTING]:
            return
        if data['finished']:
            self.stop()
            return

        self.data_lock.acquire()
        self.whitelist = data['whitelist']
        self.blacklist = data['blacklist']
        self.mime_type = data['mime_type']
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

    def kill(self):
        self._set_status(Status.KILLED)

    def run(self):
        self._set_status(Status.STARTING)
        self.web_server.start()
        self._register_to_management()
        try:
            while self._get_status() not in [Status.STOPPING, Status.KILLED]:
                # TODO: stop crawling when no links in linkdb
                if self._get_status() == Status.RUNNING:
                    for crawler in self.get_idle_crawlers():
                        package = self.get_links_package(crawler)
                        if package:
                            try:
                                r = requests.post(crawler + '/put_links', json.dumps(package))
                                self.logger.debug('Sending links to crawler %s' % crawler)
                            except ConnectionError:
                                self.ban_crawler(crawler)
                self.check_cache()
                self.check_limits()
                time.sleep(5)

            shutdown_time = time.time()
            while (time.time() - shutdown_time) < WAIT_FOR_DOWNLOAD_TIME and self.content_db.size() > 0 \
                    and self._get_status() != Status.KILLED:
                time.sleep(30)
        finally:
            self._unregister_from_management()
            self._clear()
            self.logger.debug('Stopping web interface')
            self.web_server.stop()
            self.logger.debug('Task server stopped')

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
        self.cache_lock.acquire()
        packages_cached = len(self.package_cache)
        self.cache_lock.release()
        # TODO: change following comparison - size() depends if user downloaded some data
        if (datetime.now() > expire_date) or (self.content_db.size() > max_links):
            self.logger.debug('Task limits exceeded')
            self.stop_task()
        if self.link_db.size() == 0 and packages_cached == 0:
            self.logger.debug('No links to crawl')
            self.stop_task()

    def stop_task(self):
        r = requests.post(self.manager_address + '/autoscale/server/stop_task/',
                          data={'task_id': self.task_id, 'uuid': self.uuid})
        self.logger.debug('Stopping task. Return code: %d' % r.status_code)
        if r.status_code in [status.HTTP_412_PRECONDITION_FAILED, status.HTTP_404_NOT_FOUND]:
            self.kill()

    def cache(self, package_id, crawler, links):
        self.cache_lock.acquire()
        self.package_cache[package_id] = (time.time(), links, crawler)
        self.processing_crawlers.append(crawler)
        self.cache_lock.release()
        self.logger.debug('Cached package %d' % package_id)

    def get_links_package(self, crawler):
        _links = []
        for i in range(URL_PACKAGE_SIZE):
            _links.append(self.link_db.get_link())
        _links = [link for link in _links if link]
        self.logger.debug('Retrieved %d links from linkdb' % len(_links))
        if _links:
            address = self.get_address()
            crawling_type = self.mime_type
            package_id = self.package_id
            package = {'server_address': address, 'crawling_type': crawling_type, 'id': package_id, 'links': _links}
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
                self.logger.debug('Package %d has timed out. Readding' % package_id)
                self.readd_links(self.package_cache[package_id][1])
                self.warn_crawler(self.package_cache[package_id][2])
                self.clear_cache(package_id)
        self.cache_lock.release()

    def clear_cache(self, package_id):
        self.cache_lock.acquire()
        try:
            self.processing_crawlers.remove(self.package_cache[package_id][2])
            del self.package_cache[package_id]
            self.logger.debug('Removed package %d from cache' % package_id)
        except KeyError:
            pass
        self.cache_lock.release()

    def warn_crawler(self, crawler):
        r = requests.post(self.manager_address + '/autoscale/server/warn_crawler/',
                          data={'address': crawler})
        self.logger.debug('Warning crawler %s. Return code %d' % (crawler, r.status_code))

    def ban_crawler(self, crawler):
        r = requests.post(self.manager_address + '/autoscale/server/ban_crawler/',
                          data={'address': crawler})
        self.logger.debug('Banning crawler %s. Return code %d' % (crawler, r.status_code))

    def feedback(self, regex, rate):
        # TODO: change this method to feedback regex (which will be created soon)
        #self.link_db.change_link_priority(regex, rate)
        pass

    def evaluate_link(self, link):
        domain = urlparse(link).netloc
        if not domain:
            self.logger.debug('Link evaluation failed. Bad link format: %s' % link)
            return False

        for regex in self.blacklist:
            if re.match(regex, domain):
                return False
        for regex in self.whitelist:
            if re.match(regex, domain):
                return True
        return False

    def add_links(self, links, priority, depth=0, source_url=""):
        _counter = 0
        self.logger.debug('Trying to add %d links' % len(links))
        for link in links:
            _link = URLProcessor.validate(link, source_url)
            if self.evaluate_link(_link) and not self.link_db.is_in_base(_link):
                #_depth = SimpleCrawlingDepthPolicy.calculate_depth(link, source_url, depth)
                _depth = RealDepthCrawlingDepthPolicy.calculate_depth(link, self.link_db)
                if _depth <= self.max_url_depth:
                    self.logger.debug("Added:%s with priority %d" % (_link, _depth))
                    self.link_db.add_link(_link, priority, _depth)
                    _counter += 1
        self.logger.debug("Added %d new links into DB." % _counter)

    def readd_links(self, links):
        for link in links:
            # adds link only when it was earlier in linkdb
            # TODO : ???
            self.link_db.change_link_priority(link, BerkeleyBTreeLinkDB.BEST_PRIORITY)

    def _decode_content(self, content):
        return Base64ContentCoder.decode(content)

    def put_data(self, package_id, data):
        if package_id in self.package_cache:
            self.logger.debug('Putting content from package %d' % package_id)
            self.clear_cache(package_id)
            for entry in data:
                self.logger.debug('Adding content from url %s' % entry['url'])
                self.content_db.add_content(entry['url'], entry['links'], entry['content'])
                print entry['url']
                _details = self.link_db.get_details(entry['url'])
                _url_depth = _details is not None and _details[2] or 0
                self.add_links(entry['links'], BerkeleyBTreeLinkDB.DEFAULT_PRIORITY, _url_depth, entry['url'])

    def _clear(self):
        self.link_db.clear()

    def get_data(self, size):
        """
        Returns path to file with crawling results.
        """
        self.logger.debug('Downloading content - %d size' % size)
        return self.content_db.get_file_with_data_package(size)