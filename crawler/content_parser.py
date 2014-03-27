from lxml import html


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
        pass

    def parse(self, content):
        pass


class TextHtmlParser(Parser):

    def parse(self, content):
        _dom = html.fromstring(content)
        _links = _dom.xpath('//a/@href')
        return [content, _links]