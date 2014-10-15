from url_processor import URLProcessor


class BaseCrawlingDepthPolicy(object):

    @staticmethod
    def calculate_depth():
        pass


class IgnoreDepthPolicy(BaseCrawlingDepthPolicy):
    """
    Ignores depth
    """

    @staticmethod
    def calculate_depth():
        return 0


class SimpleCrawlingDepthPolicy(BaseCrawlingDepthPolicy):
    """
    * - new domain
    1) A.com -> *B.com  => depth_2 = 0
    2) A.com -> A.com/aaa/ => depth_2 = depth_1 + 1
    3) A.com -> *B.com -> A.com/aaa/ => depth_1 = x, depth_2 = 0, depth_3 = 0
    """

    @staticmethod
    def calculate_depth(link=None, source_url=None, depth=None):
        try:
            return URLProcessor.identical_hosts(link, source_url) and int(depth) + 1 or 0
        except:
            raise ValueError('Invalid parameters.')


class RealDepthCrawlingDepthPolicy(BaseCrawlingDepthPolicy):
    """
    * - new domain
    1) A.com -> *B.com  => depth_2 = 0
    2) A.com -> A.com/aaa/ => depth_2 = depth_1 + 1
    3) A.com -> *B.com -> A.com/aaa/ => depth_1 = x, depth_2 = 0, depth_3 = x + 1
    """

    @staticmethod
    def calculate_depth(link=None, link_db=None):
        try:
            hierarchy = URLProcessor.generate_url_hierarchy(link)
            _depth = 0
            for url in hierarchy:
                if link_db.is_in_base(url):
                    _depth = max(_depth, int(link_db.get_details(url)[2]) + 1)
            return _depth
        except:
            raise ValueError('Invalid parameters.')