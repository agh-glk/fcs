from Queue import Queue
from mechanize import Browser
import string
from parser import ParserProvider
import logging


class CrawlerState:
    STARTING, WORKING, WAITING = range(3)


class Crawler():

    CONTENT_TYPE = 'content-type'
    CONTENT_LENGTH = 'content-length'
    CLIENT_VERSION = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) \
     Chrome/23.0.1271.64 Safari/537.11'

    def __init__(self, max_content_length=1024 * 1024, handle_robots=False):
        self.link_queue = Queue()
        self.max_content_length = max_content_length

        self.browser = Browser()
        self.browser.set_handle_robots(handle_robots)
        self.browser.addheaders = [('User-agent', self.__class__.CLIENT_VERSION)]

        self.logger = logging.getLogger('crawler')
        _file_handler = logging.FileHandler('crawler.log')
        _formatter = logging.Formatter('<%(asctime)s>:%(levelname)s: %(message)s')
        _file_handler.setFormatter(_formatter)
        self.logger.addHandler(_file_handler)
        self.logger.setLevel(logging.DEBUG)

    def put_into_link_queue(self, links):
        for _link in links:
            self.link_queue.put(_link)

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

    def process_one_link(self, link):
        _response = self.browser.open_novisit(link)
        _header_data = self._analyse_header(_response)
        _content_type = _header_data[self.__class__.CONTENT_TYPE]
        _parser = ParserProvider.get_parser(_content_type)
        _data = _parser.parse(_response.read())
        _data.insert(0, link)
        return _data

    def crawl(self):
        while(not self.link_queue.empty()):
            _link = None
            try:
                _link = self.link_queue.get()
                _results = self.process_one_link(_link)
                _links = _results[2]
                for l in _links:
                    print l
                print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            except Exception as e:
                self.logger.error("Exception in %s : %s" % (_link, e.message))
        self.logger.info("Crawling ended.")

    def get_state(self):
        #TODO : unregistered, starting etc. states
        if self.link_queue.empty():
            return CrawlerState.WAITING
        else:
            return CrawlerState.WORKING

if __name__ == '__main__':
    crawler = Crawler()
    crawler.put_into_link_queue(['http://onet.pl'])
    crawler.crawl()
    #print crawler.get_state()
