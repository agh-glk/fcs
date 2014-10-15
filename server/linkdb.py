import heapq
import re
import sre_constants
import threading
import bsddb3 as bsddb
from data_base_policy_module import SimplePolicyModule
import datetime
import os
import uuid
from graph_db import GraphDB


class BaseLinkDB(object):

    def is_in_base(self, link):
        pass

    def add_link(self, link, priority, depth):
        pass

    def get_link(self):
        pass

    def set_as_fetched(self, link):
        pass

    def change_link_priority(self, link, rate):
        pass

    def get_details(self, link):
        pass

    def close(self):
        pass

    def clear(self):
        pass


class GraphAndBTreeDB(BaseLinkDB):
    FOUND_LINKS_DB = "_found_links_db"
    PRIORITY_QUEUE_DB = "_priority_queue_db"

    def __init__(self, base_name, policy_module):
        self.policy_module = policy_module
        self.base_name = base_name

        self.found_links = GraphDB(base_name)

        self.priority_queue_db_name = base_name + self.__class__.PRIORITY_QUEUE_DB
        self.priority_queue = bsddb.btopen(self.priority_queue_db_name)

    def is_in_base(self, link):
        return self.found_links.is_in_base(link)

    def add_link(self, link, priority, depth):
        res = self.found_links.add_page(link, int(priority), int(depth))
        if res:
            _key = self.policy_module.generate_key(link, priority)
            self.priority_queue[_key] = link
            print "Link added: %s" % link

    def get_link(self):
        try:
            _link = self.priority_queue.first()
        except bsddb.db.DBNotFoundError:
            return None
        if _link is not None:
            del self.priority_queue[_link[0]]
            return _link[1]
        return _link

    def change_link_priority(self, link, rating):
        _old_priority = self.found_links.change_link_priority(link, rating)
        _key = self.policy_module.generate_key(link, int(_old_priority))
        if _key in self.priority_queue:
            del self.priority_queue[_key]
        _key = self.policy_module.generate_key(link, rating)
        self.priority_queue[_key] = link

    def get_details(self, link):
        return self.found_links.get_details(link)

    def points(self, url_a, url_b):
        self.found_links.points(url_a, url_b)

    def feedback(self, link, feedback_rating):
        if not self.is_in_base(link):
            print "Feedback error: Unknown link: %s" % link
            return
        _old_priority = int(self.get_details(link)[0])
        _new_priority = self.policy_module.calculate_priority(_old_priority, feedback_rating, 0)
        self.change_link_priority(link, _new_priority)
        print "Priority changed: %s %s" % (link, _new_priority)
        _visited = set([link])
        _children = set([link])
        for _depth in range(self.policy_module.get_feedback_propagation_depth()):
            _children = self.found_links.get_connected(_children)
            _children = _children - _visited
            for _child in _children:
                _old_priority = self.get_details(_child)[0]
                _new_priority = self.policy_module.calculate_priority(_old_priority, feedback_rating, _depth)
                self.change_link_priority(_child, _new_priority)
                print "Priority changed: %s %s" % (_child, _new_priority)
                _visited.add(_child)

    def size(self):
        return len(self.priority_queue)

    def close(self):
        self.priority_queue.close()

    def clear(self):
        try:
            self.close()
        except Exception as e:
            print "Link database close exception: %s" % e
        finally:
            os.remove(self.priority_queue_db_name)
            self.found_links.clear()
