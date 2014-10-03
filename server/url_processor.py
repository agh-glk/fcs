import urlparse


class URLProcessor(object):

    @staticmethod
    def validate(link, domain=None):
        _link = link.lower()
        if not _link.startswith('http://') and not _link.startswith('https://') and domain is not None:
            _link = urlparse.urljoin(domain, link)
        _link = urlparse.urldefrag(_link)[0]
        if _link[len(_link) - 1] == '/':
            _link = _link[:-1]
        return _link

    @staticmethod
    def _get_domain(link):  #TODO : zmienic nazwe na get_host_name
        return urlparse.urlparse(link)[1]

    @staticmethod
    def identical_domains(link_a, link_b):  #TODO : jw
        return URLProcessor._get_domain(link_a) == URLProcessor._get_domain(link_b)

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

if __name__ == '__main__':
    print URLProcessor._get_domain('http://allegro.pl/country_pages/1/0/z9.php')
    print URLProcessor._get_domain('http://sport.allegro.pl/country_pages/1/0/z9.php')
    u = urlparse.urlparse('http://www.allegro.pl/country_pages/1/0/z9.php')
    #u[1] = u[1].startswith('www.') and u[1][4:] or u[1]
    print u.geturl()
    print URLProcessor.generate_url_hierarchy('http://allegro.pl/country_pages/1/0/z9.php')