from graph_model import Page, Link
from bulbs.rexster import Graph, Config
import datetime


class GraphDB(object):

    def __init__(self, uri):
        self.graph = Graph(Config(uri))
        self.graph.add_proxy("pages", Page)
        self.graph.add_proxy("links", Link)

    def is_in_base(self, link):
        return self.graph.pages.index.lookup(url=link) is not None

    def add_link(self, link, priority, depth):
        return self.add_page(link, priority, depth)

    def set_as_fetched(self, link):
        page = next(self.graph.pages.index.lookup(url=link))
        page.fetch_time = datetime.datetime.now()

    def change_link_priority(self, link, rate):
        _page = next(self.graph.pages.index.lookup(url=link))
        _old_value = _page.priority
        _page.priority = rate
        return _old_value

    def get_details(self, link):
        """
        Returns list with 3 strings - priority, fetch date(could be empty string) and depth.
        """
        page = next(self.graph.pages.index.lookup(url=link))
        return map(str, [page.priority, page.fetch_time, page.depth])

    def add_page(self, link, priority, depth):
        return self.graph.pages.create(url=link, depth=depth, priority=priority)

    def _update_depth(self, url_vertex_a, url_vertex_b):
        if url_vertex_b.depth > url_vertex_a.depth + 1:
            url_vertex_b.depth = url_vertex_a.depth+1
            for url_vertex in url_vertex_b.outE():
                self._update_depth(url_vertex_b, url_vertex)

    def points(self, url_a, url_b):
        url_a_vertex = next(self.graph.pages.index.lookup(url=url_a))
        url_b_vertex = next(self.graph.pages.index.lookup(url=url_b))
        _edge = self.graph.links.create(url_a_vertex, url_b_vertex)
        self._update_depth(url_a_vertex, url_b_vertex)
        return _edge

    def get_pages_proxy(self):
        return self.graph.pages

    def get_links_proxy(self):
        return self.graph.links

    def clear(self):
        self.graph.clear()


if __name__ == '__main__':
    gdb = GraphDB("http://localhost:8182/graphs/linkgraph")
    link_one = "http://link_one.pl"
    link_two = "http://link_two.pl"
    link_one_vertex = gdb.add_page(link_one, 0, 1)
    link_two_vertex = gdb.add_page(link_two, 2, 3)
    print link_one_vertex.depth
    print link_one_vertex.priority
    gdb.points(link_one, link_two)