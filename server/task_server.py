import json
import logging
import re
import threading
import thread
import time
import sys
from urlparse import urlparse
import requests
from requests.exceptions import ConnectionError
from rest_framework import status
from link_db import GraphAndBTreeDB
from data_base_policy_module import SimplePolicyModule
from content_db import BerkeleyContentDB
from django.utils.timezone import datetime
from url_processor import URLProcessor
from crawling_depth_policy import SimpleCrawlingDepthPolicy, RealDepthCrawlingDepthPolicy, IgnoreDepthPolicy


sys.path.append('../')
from common.content_coder import Base64ContentCoder


URL_PACKAGE_TIMEOUT = 60
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
WAIT_FOR_DOWNLOAD_TIME = 25    # in seconds
DATA_PACKAGE_SIZE = 5
KEEP_STATS_SECONDS = 900
CRAWLING_PERIOD = 60


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
        self.statistics_lock = threading.RLock()

        self.web_server = web_server
        self.manager_address = manager_address
        self.link_db = GraphAndBTreeDB('link_db_task_'+str(task_id), SimplePolicyModule)
        self.content_db = BerkeleyContentDB('content_db_task_'+str(task_id))

        self.crawlers = {}
        self.task_id = task_id
        self.max_links = 0
        self.expire_date = None
        self.mime_type = []
        self.uuid = ''
        self.whitelist = []
        self.blacklist = []
        self.urls_per_min = 0

        self.package_cache = {}
        self.package_id = 0
        self.processing_crawlers = []
        self.max_url_depth = max_url_depth
        
        self.status = Status.INIT

        self.crawled_links = []
        self.stats_reset_time = time.time()

        self.logger = logging.getLogger('server')
        _file_handler = logging.FileHandler('server%s.log' % task_id)
        _formatter = logging.Formatter('<%(asctime)s>:%(levelname)s: %(message)s')
        _file_handler.setFormatter(_formatter)
        self.logger.addHandler(_file_handler)
        self.logger.setLevel(logging.DEBUG)

    def assign_crawlers(self, assignment):
        """
        Sets actual crawler assignment.

        Task server can send crawling requests only to these crawlers
        and size of packages must be specified in assignment dict for each crawler.
        It allows to control crawling efficiency of all task servers.
        """
        self.data_lock.acquire()
        self.crawlers = assignment
        self.data_lock.release()
        self.logger.debug('%d crawlers assigned' % len(assignment))

    def assign_speed(self, speed):
        """
        Sets task server's crawling speed.

        After each speed change statistics are reset.
        """
        self.data_lock.acquire()
        self.urls_per_min = int(speed)
        self._reset_stats()
        self.data_lock.release()
        self.logger.debug('Changed speed to %d', self.urls_per_min)

    def get_address(self):
        return 'http://' + self.web_server.get_host()

    def _set_status(self, status):
        """
        Sets task server state.
        """
        self.status_lock.acquire()
        self.status = status
        self.status_lock.release()
        self.logger.debug('Changed status to: %d' % status)

    def _get_status(self):
        """
        Returns actual task server state.
        """
        self.status_lock.acquire()
        _status = self.status
        self.status_lock.release()
        return _status

    def _register_to_management(self):
        """
        Sends register request to FCS main application.

        Received data is used to set crawling parameters.
        """
        r = requests.post(self.manager_address + '/autoscale/server/register/',
                          data={'task_id': self.task_id, 'address': self.get_address()})
        self.logger.debug('Registering to management. Return code: %d, message: %s' % (r.status_code, r.content))
        if r.status_code in [status.HTTP_412_PRECONDITION_FAILED, status.HTTP_404_NOT_FOUND]:
            self.stop()
            return

        self._set_status(Status.RUNNING)
        try:
            data = r.json()
            self.update(data)
            self.add_links(data['start_links'], self.link_db.policy_module.DEFAULT_PRIORITY, 0)
            self.data_lock.acquire()
            self.uuid = data['uuid']
            self.data_lock.release()
            self.logger.debug('Registered to management')
        except (KeyError, ValueError) as e:
            self.logger.debug('Error while registering: %s' % str(e))
            self.stop()

    def _unregister_from_management(self):
        """
        Sends unregister request to FCS main application.
        """
        r = requests.post(self.manager_address + '/autoscale/server/unregister/',
                          data={'task_id': self.task_id, 'uuid': self.uuid})
        self.logger.debug('Unregistering from management. Return code: %d, message: %s' % (r.status_code, r.content))

    def update(self, data):
        """
        Updates crawling parameters and status.

        It is called usually when user makes some changes in task data using GUI or API.
        """
        self.logger.debug('Updating task server: %s' % json.dumps(data))
        if self._get_status() in [Status.STOPPING, Status.STARTING]:
            return
        if data['finished']:
            self.stop()
            return

        self.data_lock.acquire()
        self.whitelist = data['whitelist']
        self.blacklist = data['blacklist']
        self.mime_type = data['mime_type']
        self.max_links = int(data['max_links'])
        self.expire_date = datetime.strptime(data['expire_date'], DATE_FORMAT)
        self.data_lock.release()

        if data['active']:
            self.resume()
        else:
            self.pause()

    def pause(self):
        """
        Pauses task server if it was running.
        """
        if self._get_status() == Status.RUNNING:
            self._set_status(Status.PAUSED)

    def resume(self):
        """
        Resumes task server if it was paused.
        """
        if self._get_status() == Status.PAUSED:
            self._set_status(Status.RUNNING)

    def stop(self):
        """
        Sets STOPPING status

        Task server in this state won't send crawling requests anymore.
        It will wait WAIT_FOR_DOWNLOAD_TIME seconds for user to download gathered data.
        """
        self._set_status(Status.STOPPING)

    def kill(self):
        """
        Sets KILLED status

        Task server in this state will be stopped as soon as possible
        """
        self._set_status(Status.KILLED)
        self._clear()

    def run(self):
        """
        Main task server loop
        """
        self._set_status(Status.STARTING)
        self.web_server.start()
        self._register_to_management()
        try:
            while self._get_status() not in [Status.STOPPING, Status.KILLED]:
                if self._get_status() == Status.RUNNING and not self._efficiency_achieved():
                    for crawler in self.get_idle_crawlers():
                        package = self._get_links_package(crawler, self.crawlers[crawler])
                        if package:
                            try:
                                requests.post(crawler + '/put_links', json.dumps(package))
                                self.logger.debug('Sending links to crawler %s' % crawler)
                            except ConnectionError:
                                pass
                self._check_cache()
                self._check_limits()
                self._clear_stats()
                time.sleep(1)

            shutdown_time = time.time()
            while (time.time() - shutdown_time) < WAIT_FOR_DOWNLOAD_TIME and self.content_db.size() > 0 \
                    and self._get_status() != Status.KILLED:
                time.sleep(30)
        except:
            raise
        finally:
            self._unregister_from_management()
            self._clear()
            self.logger.debug('Stopping web interface')
            self.web_server.stop()
            self.logger.debug('Task server stopped')

    def get_idle_crawlers(self):
        """
        Returns list of crawlers which are not processing any requests.
        """
        self.data_lock.acquire()
        crawlers = self.crawlers
        self.data_lock.release()
        self.cache_lock.acquire()
        processing = self.processing_crawlers
        self.cache_lock.release()
        return [crawler for crawler in crawlers if crawler not in processing]

    def _check_limits(self):
        """
        Checks if crawling limits are exceeded or no link left to crawl.
        If so, tries to stop task.
        """
        self.data_lock.acquire()
        expire_date = self.expire_date
        max_links = self.max_links
        self.data_lock.release()
        self.cache_lock.acquire()
        packages_cached = len(self.package_cache)
        self.cache_lock.release()
        if datetime.now() > expire_date:
            self.logger.debug('Task expired')
            self._stop_task()
        elif self.content_db.added_records_num() > max_links:
            self.logger.debug('Task max links limit exceeded')
            self._stop_task()
        elif self.link_db.size() == 0 and packages_cached == 0:
            self.logger.debug('No links to crawl')
            self._stop_task()

    def _stop_task(self):
        """
        Sends request to FCS main application to stop this task server's task.

        If case of error task server will be killed.
        """
        r = requests.post(self.manager_address + '/autoscale/server/stop_task/',
                          data={'task_id': self.task_id, 'uuid': self.uuid})
        self.logger.debug('Stopping task. Return code: %d, message: %s' % (r.status_code, r.content))
        if r.status_code in [status.HTTP_412_PRECONDITION_FAILED, status.HTTP_404_NOT_FOUND]:
            self.kill()

    def _cache(self, package_id, crawler, links):
        """
        Puts link package into cache and marks assigned crawler as 'processing'
        """
        self.cache_lock.acquire()
        has_timed_out = False
        self.package_cache[package_id] = [time.time(), links, crawler, has_timed_out]
        self.processing_crawlers.append(crawler)
        self.cache_lock.release()
        self.logger.debug('Cached package %d' % package_id)

    def _get_links_package(self, crawler, size):
        """
        Prepares link package of given size for given crawler and caches it.
        """
        _links = []
        for i in range(size):
            _links.append(self.link_db.get_link())
        _links = [link for link in _links if link]
        self.logger.debug('Retrieved %d links from linkdb' % len(_links))
        if _links:
            address = self.get_address()
            package_id = self.package_id
            package = {'server_address': address, 'mime_type': self.mime_type, 'id': package_id, 'links': _links}
            self._cache(package_id, crawler, _links)
            self.package_id += 1
            return package
        else:
            return None

    def _check_cache(self):
        """
        Scans package cache looking for timed out packages.

        Marks timed out packages as such
        and again puts links that they contained into database.
        """
        cur_time = time.time()
        self.cache_lock.acquire()
        for package_id in self.package_cache.keys():
            if (cur_time - self.package_cache[package_id][0] > URL_PACKAGE_TIMEOUT) and \
                    not self.package_cache[package_id][3]:
                self.logger.debug('Package %d has timed out. Readding' % package_id)
                self.package_cache[package_id][3] = True
            elif (cur_time - self.package_cache[package_id][0]) > 5 * URL_PACKAGE_TIMEOUT:
                self._clear_cache(package_id)
        self.cache_lock.release()

    def _clear_cache(self, package_id):
        """
        Removes entry from package cache for given package id.

        It also marks crawler which was assigned to this crawling request as 'idle'
        so next request can be sent to this crawler.
        """
        self.cache_lock.acquire()
        try:
            self.processing_crawlers.remove(self.package_cache[package_id][2])
            del self.package_cache[package_id]
            self.logger.debug('Removed package %d from cache' % package_id)
        except KeyError:
            pass
        self.cache_lock.release()

    def feedback(self, link, rating):
        """
        Increases priority of specified link and his children.
        """
        self.logger.debug("Feedback: %s %s" % (link, rating))
        thread.start_new_thread(self.link_db.feedback, (link, rating))

    def _evaluate_link(self, link):
        """
        Checks blacklist and whitelist and decides
        if link can be put into link queue.
        """
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
            if self._evaluate_link(_link) and not self.link_db.is_in_base(_link):
                #_depth = SimpleCrawlingDepthPolicy.calculate_depth(link, source_url, depth) usage example
                #_depth = RealDepthCrawlingDepthPolicy.calculate_depth(link, self.link_db) usage example
                _depth = IgnoreDepthPolicy.calculate_depth()
                if _depth <= self.max_url_depth:
                    try:
                        self.link_db.add_link(_link, priority, _depth)
                        if source_url:
                            self.link_db.points(source_url, _link)
                    except Exception as e:
                        self.logger.error("Add links error:"+str(_link)+"Message:"+str(e.message))
                        print "Add links error:" + str(_link) + "Message:" + str(e.message)
                    else:
                        self.logger.debug("Added:%s with priority %s" % (_link, priority))
                        _counter += 1
        self.logger.debug("Added %d new links into DB." % _counter)

    def _decode_content(self, content):
        return Base64ContentCoder.decode(content)

    def put_data(self, package_id, data):
        """
        Handles data package received from crawler and puts it into content database

        If received package isn't in package cache (or crawling request has timed out)
        no data will be stored in database.
        It also marks crawler which was assigned to this crawling request as 'idle'
        so next request can be sent to this crawler.
        """
        if package_id in self.package_cache:
            has_timed_out = self.package_cache[package_id][3]
            if not has_timed_out:
                self.logger.debug('Putting content from package %d' % package_id)
                start_time = self.package_cache[package_id][0]
                end_time = time.time()
                self._add_stats(start_time, end_time, len(data))
                for entry in data:
                    self.logger.debug('Adding content from url %s' % entry['url'])
                    self.content_db.add_content(entry['url'], entry['links'], entry['content'])
                    _details = self.link_db.get_details(entry['url'])
                    _url_depth = _details is not None and _details[2] or 0
                    #TODO - FUTURE WORKS: inherited priority?
                    self.add_links(entry['links'], self.link_db.policy_module.DEFAULT_PRIORITY, _url_depth,
                                   entry['url'])
            self._clear_cache(package_id)

    def _clear(self):
        """
        Clears database files
        """
        self.logger.debug('Clearing db files')
        try:
            self.content_db.clear()
            self.link_db.clear()
        except Exception as e:
            self.logger.error(e)

    def get_data(self, size):
        """
        Returns path to file with crawling results.
        """
        self.logger.debug('Downloading content - %d size' % size)
        return self.content_db.get_file_with_data_package(size)

    def _add_stats(self, start_time, end_time, links):
        """
        Adds new statistics entry - links number with current time
        """
        self.statistics_lock.acquire()
        self.crawled_links.append((start_time, end_time, links))
        self.statistics_lock.release()

    def _reset_stats(self):
        """
        Removes all statistics entries and
        resets time from which statistics can be measured.
        """
        self.statistics_lock.acquire()
        self.crawled_links = []
        self.stats_reset_time = time.time()
        self.statistics_lock.release()

    def _get_stats(self, seconds):
        """
        Returns statistics summarise for the last seconds in a dict.

        Dict keys:
        'seconds' - actual number of seconds for which measurement was done
        'links' - number of links crawled during this time
        'speed' - crawling speed assigned to this task server
        """
        self.statistics_lock.acquire()
        now = time.time()
        from_time = now - seconds
        if self.stats_reset_time > from_time:
            from_time = self.stats_reset_time

        links = 0
        for entry in self.crawled_links:
            if entry[0] > from_time:
                links += entry[2]
            elif entry[1] > from_time:
                links += int(entry[2] * (entry[1] - from_time) / (entry[1] - entry[0]))
        self.statistics_lock.release()

        ret = dict()
        ret['seconds'] = int(now - from_time)
        ret['links'] = links
        self.data_lock.acquire()
        ret['urls_per_min'] = self.urls_per_min
        self.data_lock.release()
        return ret

    def _clear_stats(self):
        """
        Removes statistics entries which are too old
        """
        self.statistics_lock.acquire()
        from_time = max(time.time() - KEEP_STATS_SECONDS, self.stats_reset_time)
        index = 0
        for i in range(len(self.crawled_links)):
            if self.crawled_links[i][0] > from_time:
                index = i
                break
        self.crawled_links = self.crawled_links[index:]
        self.stats_reset_time = from_time
        self.statistics_lock.release()

    def _efficiency_achieved(self):
        """
        Checks if crawled links number in the last time is above expectation.
        """
        stats = self._get_stats(CRAWLING_PERIOD)
        if stats['seconds'] > 0:
            return 60. * stats['links'] / stats['seconds'] >= stats['urls_per_min']
        return False