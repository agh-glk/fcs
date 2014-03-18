from Queue import Queue
from mechanize import Browser
import string
from parser import ParserProvider
import logging

from threading import Lock
from thread_with_exc import ThreadWithExc


class CrawlerState:
    STARTING, WORKING, WAITING = range(3)


class Crawler(ThreadWithExc):

    CONTENT_TYPE = 'content-type'
    CONTENT_LENGTH = 'content-length'
    CLIENT_VERSION = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) \
     Chrome/23.0.1271.64 Safari/537.11'

    def __init__(self, event, max_content_length=1024 * 1024, handle_robots=False):
        super(Crawler, self).__init__()
        self.link_package_queue = Queue()
        self.max_content_length = max_content_length

        self.browser = Browser()
        self.browser.set_handle_robots(handle_robots)
        self.browser.addheaders = [('User-agent', self.__class__.CLIENT_VERSION)]

        self.event = event
        self.exit_flag_lock = Lock()
        self.exit_flag = False

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

    def _process_one_link(self, link):
        _response = self.browser.open_novisit(link)
        _header_data = self._analyse_header(_response)
        _content_type = _header_data[self.__class__.CONTENT_TYPE]
        _parser = ParserProvider.get_parser(_content_type)
        _data = _parser.parse(_response.read())
        _data.insert(0, link)
        return _data

    def _crawl(self):
        while not self.link_package_queue.empty() and not self._get_exit_flag():

            _final_results = []
            (_id, _server_address, _crawling_policy, _links) = self.link_package_queue.get()
            for _link in _links:

                try:
                    _results = self._process_one_link(_link)
                    _final_results.append(_results)
                    _extracted_links = _results[2]
                    for l in _extracted_links:
                        print l
                    print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
                except Exception as e:
                    self.logger.error("Exception in %s : %s" % (_link, e.message))
                    _results = None
                _final_results.append(_results)
            self.logger.info("Crawling package from %s ended." % _server_address)
            self._send_results_to_task_server(_server_address, _id, _final_results)

    def _send_results_to_task_server(self, package_id, server_address, results):
        self.logger.info("Data send to Task Server.")

    def _get_exit_flag(self):
        self.exit_flag_lock.acquire()
        _should_stop = self.exit_flag
        self.exit_flag_lock.release()
        return _should_stop

    def get_state(self):
        #TODO : unregistered, starting etc. states
        if self.link_package_queue.empty():
            return CrawlerState.WAITING
        else:
            return CrawlerState.WORKING

    def stop(self):
        self.exit_flag_lock.acquire()
        self.exit_flag = True
        self.exit_flag_lock.release()

    def kill(self):
        self.raise_exc(KeyboardInterrupt)

    def run(self):
        self.event.wait()
        while not self._get_exit_flag():
            if self.event.isSet():
                self._crawl()
                self.event.clear()
            else:
                self.event.wait()
        print "Crawler stop"



