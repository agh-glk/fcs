from Queue import Queue
from mechanize import Browser
import string
from requests.exceptions import ConnectionError
from rest_framework import status
import time
from content_parser import ParserProvider
import logging
import requests
import json

from threading import Lock, RLock
from thread_with_exc import ThreadWithExc
from mime_content_type import MimeContentType


KEEP_STATS_SECONDS = 900


class CrawlerState:
    STARTING, WORKING, WAITING = range(3)


class Crawler(ThreadWithExc):

    CONTENT_TYPE = 'content-type'
    CONTENT_LENGTH = 'content-length'
    CLIENT_VERSION = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) \
     Chrome/23.0.1271.64 Safari/537.11'

    def __init__(self, web_server, event, port, manager_address, max_content_length=1024 * 1024, handle_robots=False):
        super(Crawler, self).__init__()
        self.link_package_queue = Queue()
        self.max_content_length = max_content_length

        self.browser = Browser()
        self.browser.set_handle_robots(handle_robots)
        self.browser.addheaders = [('User-agent', self.__class__.CLIENT_VERSION)]

        self.event = event
        self.exit_flag_lock = Lock()
        self.exit_flag = False

        self.uuid = ''
        self.manager_address = manager_address
        self.port = port
        self.web_server = web_server

        self.stats_lock = RLock()
        self.stats_reset_time = time.time()
        self.crawled_links = []

        self.logger = logging.getLogger('crawler')
        _file_handler = logging.FileHandler('crawler.log')
        _formatter = logging.Formatter('<%(asctime)s>:%(levelname)s: %(message)s')
        _file_handler.setFormatter(_formatter)
        self.logger.addHandler(_file_handler)
        self.logger.setLevel(logging.DEBUG)

    def put_into_link_queue(self, link_package):
        self.link_package_queue.put(link_package)

    def _analyse_header(self, response):
        _header = response.info()
        _header_dict = dict(zip(map(string.lower, _header.keys()), _header.values()))
        result = {}
        try:
            _content_length = _header_dict.__contains__(self.__class__.CONTENT_TYPE)
            if _content_length > self.max_content_length:
                raise Exception("'Content length' too big")
        except KeyError:
            raise Exception("'Content-length' unknown")
        try:
            _content_type = _header_dict[self.__class__.CONTENT_TYPE]
            result[self.__class__.CONTENT_TYPE] = _content_type
        except Exception:
            raise Exception("'Content-type' unknown")
        return result

    def _process_one_link(self, link, mime_types):
        _response = self.browser.open_novisit(link)
        _header_data = self._analyse_header(_response)
        _content_type = _header_data[self.__class__.CONTENT_TYPE]
        if not MimeContentType(_content_type).one_of(mime_types):
            raise Exception("Page skipped because does not meet MIME content type criteria.")
        _parser = ParserProvider.get_parser(_content_type)
        _data = _parser.parse(_response.read(), url=link)
        _results = dict()
        _results["url"] = link
        _results["content"], _results["links"] = (_data[0], _data[1])
        return _results

    def _crawl(self):
        while not self.link_package_queue.empty() and not self._get_exit_flag():
            start_time = time.time()
            _final_results = []
            (_id, _server_address, _mime_types, _links) = self.link_package_queue.get()
            _mime_types = [MimeContentType(x) for x in _mime_types]
            for _link in _links:
                self.logger.info("Processing url %s started..." % _link)
                try:
                    _results = self._process_one_link(_link, _mime_types)
                except Exception as e:
                    self.logger.error("Exception in %s : %s" % (_link, e.message))
                    _results = {"url": _link, "links": [], "content": ""}
                else:
                    self.logger.info("Processing url %s ended successfully. %s urls extracted" %
                                 (_link, len(_results['links'])))
                _final_results.append(_results)

            self.logger.info("Crawling package from %s ended." % _server_address)
            self._send_results_to_task_server(_id, _server_address, _final_results)
            end_time = time.time()
            self.add_stats(start_time, end_time, len(_final_results))

    def add_stats(self, start_time, end_time, links_num):
        self.stats_lock.acquire()
        self.crawled_links.append((start_time, end_time, links_num))
        self.stats_lock.release()

    def clear_stats(self):
        self.stats_lock.acquire()
        from_time = max(time.time() - KEEP_STATS_SECONDS, self.stats_reset_time)
        index = 0
        for i in range(len(self.crawled_links)):
            if self.crawled_links[i][0] > from_time:
                index = i
                break
        self.crawled_links = self.crawled_links[index:]
        self.stats_reset_time = from_time
        self.stats_lock.release()

    def get_stats(self, seconds):
        self.stats_lock.acquire()
        now = time.time()
        from_time = now - seconds
        if self.stats_reset_time > from_time:
            from_time = self.stats_reset_time

        links = 0
        load_time = 0
        for entry in self.crawled_links:
            if entry[0] > from_time:
                links += entry[2]
                load_time += entry[1] - entry[0]
        self.stats_lock.release()

        ret = dict()
        ret['seconds'] = int(now - from_time)
        ret['links'] = links
        ret['load'] = int(load_time)
        return ret

    def _send_results_to_task_server(self, package_id, server_address, results):
        try:
            requests.post(server_address + '/put_data', json.dumps({"id": package_id, "data": results}))
            self.logger.info("Data send to Task Server.")
        except ConnectionError as e:
            self.logger.exception(e)

    def _get_exit_flag(self):
        self.exit_flag_lock.acquire()
        _should_stop = self.exit_flag
        self.exit_flag_lock.release()
        return _should_stop

    def _register_to_management(self):
        r = requests.post(self.manager_address + '/autoscale/crawler/register/',
                          data={'address': self.get_address()})
        if r.status_code == status.HTTP_409_CONFLICT:
            self.kill()
            return

        data = r.json()
        self.uuid = data['uuid']

    def _unregister_from_management(self):
        requests.post(self.manager_address + '/autoscale/crawler/unregister/',
                      data={'uuid': self.uuid})

    def get_address(self):
        return 'http://localhost:' + str(self.port)

    def get_state(self):
        #TODO : unregistered, starting etc. states
        if self.link_package_queue.empty():
            return CrawlerState.WAITING
        else:
            return CrawlerState.WORKING

    def stop(self):
        self.exit_flag_lock.acquire()
        self.exit_flag = True
        self.logger.debug('Exit flag set true')
        self.exit_flag_lock.release()

    def kill(self):
        self.raise_exc(KeyboardInterrupt)

    def run(self):
        self._register_to_management()
        self.event.wait()
        try:
            while not self._get_exit_flag():
                if self.event.isSet():
                    self._crawl()
                    self.event.clear()
                    self.clear_stats()
                else:
                    self.event.wait()
        finally:
            self.logger.debug('Finishing crawler')
            self._unregister_from_management()
            self.web_server.kill()
        print "Crawler stop"

if __name__ == '__main__':
    cr = Crawler(None)
    #cr._process_one_link('https://github.com/repo/afasf', 0)
    cr._process_one_link('http://127.0.0.1:8080', 0)
