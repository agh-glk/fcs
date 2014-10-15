import urlparse


class URLProcessor(object):

    @staticmethod
    def validate(link, domain=None):
        _link = link.lower().strip()
        if _link.startswith('http://www.'):
            _link = _link.replace('http://www.', 'http://')
        if _link.startswith('https://www.'):
            _link = _link.replace('https://www.', 'https://')
        if not _link.startswith('http://') and not _link.startswith('https://') and domain is not None:
            _link = urlparse.urljoin(domain, link)
        _link = urlparse.urldefrag(_link)[0]
        if _link[len(_link) - 1] == '/':
            _link = _link[:-1]
        return _link

    @staticmethod
    def _get_host_name(link):
        return urlparse.urlparse(link)[1]

    @staticmethod
    def identical_hosts(link_a, link_b):
        return URLProcessor._get_host_name(link_a) == URLProcessor._get_host_name(link_b)

    @staticmethod
    def generate_url_hierarchy(link):
        hierarchy = []
        url = urlparse.urlparse(link)
        _scheme, _domain, _path = url[0], url[1], url[2].split('/')[1:-1]
        hierarchy.append(_domain)
        for index, item in enumerate(_path):
            hierarchy.append(hierarchy[index]+"/"+item)
        hierarchy = map(lambda x: "%s://%s" % (_scheme, x), hierarchy)
        return hierarchy