import urlparse


class URLProcessor(object):

    @staticmethod
    def process(link, domain=None):
        _link = link.strip().lower()
        if not link.startswith('http://') and not link.startswith('https://') and domain is not None:
            _link = urlparse.urljoin(domain, link)
        _link = urlparse.urldefrag(_link)[0]
        if _link[len(_link) - 1] == '/':
            _link = _link[:-1]
        return _link