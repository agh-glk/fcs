import datetime
import shutil
import os


class GraphDB(object):

    def __init__(self, location):
        try:
            import jpype
            from neo4j import GraphDatabase
            jpype.attachThreadToJVM()
        except Exception:
            raise
        self.location = os.path.join(os.getcwd(), location)
        if os.path.isdir(self.location):
            shutil.rmtree(self.location, True)
        self.graph = GraphDatabase(location)

        with self.graph.transaction:
            self.pages = self.graph.node()
            self.graph.reference_node.PAGES(self.pages)

            PAGES_INDEX = "pages"
            if self.graph.node.indexes.exists(PAGES_INDEX) == 0:
                self.pages_idx = self.graph.node.indexes.create(PAGES_INDEX)
            else:
                self.pages_idx = self.graph.node.indexes.get(PAGES_INDEX)
        print 'Done'

    def check_if_attached_to_jvm(function):
        def wrapped(*args):
            import jpype
            if (not jpype.isThreadAttachedToJVM()):
                jpype.attachThreadToJVM()
            return function(*args)
        return wrapped

    @check_if_attached_to_jvm
    def is_in_base(self, link):
        return self._find_pages(link) is not None

    @check_if_attached_to_jvm
    def add_link(self, link, priority, depth):
        return self.add_page(link, priority, depth)

    @check_if_attached_to_jvm
    def set_as_fetched(self, link):
        page = self._find_pages(link)
        with self.graph.transaction:
            page['fetch_time'] = datetime.datetime.now()

    @check_if_attached_to_jvm
    def change_link_priority(self, link, rate):
        _page = self._find_pages(link)
        if _page:
            _old_value = _page['priority']
            with self.graph.transaction:
                _page['priority'] = rate
            return _old_value

    @check_if_attached_to_jvm
    def get_details(self, link):
        """
        Returns list with 3 strings - priority, fetch date(could be empty string) and depth.
        """
        _page = self._find_pages(link)
        if _page:
            return map(str, [_page['priority'], _page['fetch_time'], _page['depth']])
        raise Exception("Page not found!")

    @check_if_attached_to_jvm
    def add_page(self, link, priority, depth):
        if(not self.is_in_base(link)):
            with self.graph.transaction:
                page = self.graph.node(url=link, priority=priority, depth=depth, fetch_time="")
                page.INSTANCE_OF(self.pages)
                self.pages_idx['url'][link] = page
                return page
        return None

    def _update_depth(self, url_vertex_a, url_vertex_b):
        if url_vertex_b['depth'] > url_vertex_a['depth'] + 1:
            url_vertex_b['depth'] = url_vertex_a['depth'] + 1
            if len(url_vertex_b.links.outgoing) > 0:
                for url_vertex in url_vertex_b.links.outgoing:
                    self._update_depth(url_vertex_b, url_vertex)

    def _find_pages(self, link):
        try:
            return self.pages_idx['url'][link].single
        except ValueError:
            return None

    @check_if_attached_to_jvm
    def points(self, url_a, url_b):
        page_a_vertex = self._find_pages(url_a)
        page_b_vertex = self._find_pages(url_b)
        if page_a_vertex and page_b_vertex:
            with self.graph.transaction:
                _edge = page_a_vertex.links(page_b_vertex)
                self._update_depth(page_a_vertex, page_b_vertex)
            return _edge

    @check_if_attached_to_jvm
    def get_connected(self, links):
        _res = []
        for _link in links:
            page_vertex = self._find_pages(_link)
            if page_vertex:
                _res = _res + [x.end['url'] for x in page_vertex.links.outgoing]
        return set(_res)

    def clear(self):
        shutil.rmtree(self.location, True)