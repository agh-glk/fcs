from bs4 import BeautifulSoup
import logging
import urlparse
from mechanize import Browser


class ParserProvider():

    parsers = {}

    @staticmethod
    def get_parser(content_type):
        _content_type = content_type.split(';')[0]
        if ParserProvider.parsers.__contains__(_content_type):
            return ParserProvider.parsers[_content_type]
        else:
            _class_name = ''.join([x.title() for x in _content_type.split('/')])+'Parser'
            instance = None
            try:
                instance = getattr(__import__(ParserProvider.__module__), _class_name)()
            except Exception:
                raise Exception("Unknown parser type")
            ParserProvider.parsers[_content_type] = instance
            return instance


class Parser():
    def __init__(self):
        self.logger = logging.getLogger('parser')
        _file_handler = logging.FileHandler('crawler.log')
        _formatter = logging.Formatter('<%(asctime)s>:%(levelname)s: %(message)s')
        _file_handler.setFormatter(_formatter)
        self.logger.addHandler(_file_handler)
        self.logger.setLevel(logging.DEBUG)

    def parse(self, content, policy=None, url=""):
        pass


class TextHtmlParser(Parser):

    PARSER_TYPE = "lxml"

    def _get_encoding(self, soup):
        _encodings = [x["charset"] for x in soup.head.find_all('meta') if "charset" in x.attrs.keys()]
        if len(_encodings) > 0:
            return _encodings[0]
        return "utf8"

    def _find_links_witha_href(self, soup, url, encoding):
        _results = []
        for tag in soup.findAll('a', href=True):
            try:
                _link = urlparse.urljoin(url, unicode(tag['href'], encoding=encoding))
                _results.append(_link)
            except Exception:
                self.logger.error("Exception during parsing "+str(tag))
        return _results

    def parse(self, content, policy=None, url=""):
        _soup = BeautifulSoup(content, self.__class__.PARSER_TYPE)
        _links = []
        _encoding = self._get_encoding(_soup)
        _links.append(self._find_links_witha_href(_soup, url, _encoding))
        return [unicode(content, encoding=_encoding), _links]





