import heapq
import re
import threading
import bsddb
from key_policy_module import SimpleKeyPolicyModule
import datetime
import os


class BaseLinkDB(object):

    def is_in_base(self, link):
        pass

    def add_link(self, link, priority, depth):
        pass

    def get_link(self):
        pass

    def set_as_fetched(self, link):
        pass

    def feedback(self, link, rate):
        pass

    def get_details(self, link):
        pass

    def close(self):
        pass

    def clear(self):
        pass


class SimpleLinkDB(BaseLinkDB):

    BEST_PRIORITY = 0
    WORST_PRIORITY = 10
    START_PRIORITY = 5

    def __init__(self):
        self.lock = threading.Lock()
        self.counter = 0
        self.db = []
        self.links = set()
        self.rating = {}

    def add_links(self, links, default_priority=None, force=False):
        _priority = default_priority or self.__class__.START_PRIORITY
        self.lock.acquire()
        for link in links:
            self._add_link(link, _priority, force)
        self.lock.release()

    def _add_link(self, link, default_priority, force):
        if (not force) and (link in self.links):
            return
        self.links.add(link)
        priority = self.evaluate(link, default_priority)
        heapq.heappush(self.db, (priority, self.counter, link))
        self.counter += 1

    def _get_link(self):
        link = heapq.heappop(self.db)[2]
        return link

    def get_links(self, number):
        links = []
        self.lock.acquire()
        try:
            for i in range(number):
                links.append(self._get_link())
        except IndexError:
            pass
        self.lock.release()
        return links

    #TODO: remove
    def content(self):
        return self.db

    def feedback(self, regex, rate):
        self.lock.acquire()
        self.rating[regex] = rate
        for i in range(len(self.db)):
            entry = self.db[i]
            self.db[i] = (self.evaluate(entry[2], entry[0]), entry[1], entry[2])
        heapq.heapify(self.db)
        self.lock.release()

    def evaluate(self, link, default):
        priorities = []
        for regex in self.rating:
            if re.match(regex, link):
                priorities.append(self.rating[regex])
        if priorities:
            return sorted(priorities)[-1]  # worst possible priority
        else:
            return default


class BerkeleyBTreeLinkDB(BaseLinkDB):

    FOUND_LINKS_DB = "_found_links_db"
    PRIORITY_QUEUE_DB = "_priority_queue_db"

    DEFAULT_PRIORITY = 500
    BEST_PRIORITY = 0

    def __init__(self, base_name, policy_module):
        self.policy_module = policy_module
        self.base_name = base_name

        self.found_links = bsddb.btopen(base_name+self.__class__.FOUND_LINKS_DB)
        self.priority_queue = bsddb.btopen(base_name+self.__class__.PRIORITY_QUEUE_DB)

    def is_in_base(self, link):
        return str(link) in self.found_links

    def add_link(self, link, priority, depth):
        self.found_links[str(link)] = ";".join([str(priority), "", str(depth)])
        _key = self.policy_module.generate_key(link, priority)
        self.priority_queue[_key] = link

    def get_link(self):
        try:
            _link = self.priority_queue.first()
        except bsddb.db.DBNotFoundError:
            return None
        if _link is not None:
            del self.priority_queue[_link[0]]
            return _link[1]
        return _link

    def set_as_fetched(self, link):
        _data = self.found_links.get(link).split(';')
        _data[1] = str(datetime.datetime.now())
        self.found_links[str(link)] = ";".join(_data)

    def feedback(self, link, rate):
        _details = self.found_links[str(link)]
        _old_priority = _details.split(';')[0]
        _key = self.policy_module.generate_key(link, int(_old_priority))
        del self.priority_queue[_key]
        self.add_link(link, rate, _details[0])

    def get_details(self, link):
        return self.found_links.get(link).split(';')

    def close(self):
        self.found_links.close()
        self.priority_queue.close()

    def clear(self):
        self.close()
        os.remove(self.base_name+self.__class__.FOUND_LINKS_DB)
        os.remove(self.base_name+self.__class__.PRIORITY_QUEUE_DB)

    def _print_db(self, data_base):
        print '--------------'
        print data_base.items()
        print '=============='

    def _print(self):
        self._print_db(self.priority_queue)
        self._print_db(self.found_links)


if __name__ == '__main__':

    links_db = BerkeleyBTreeLinkDB("db_name", SimpleKeyPolicyModule)
    links = ["www.zzz.com", 'aaaa.pl', 'azadsafsdgsdgsdgdsg.com', '124edeasf23rdgfsdg.org']
    for i in range(10*100*100*100):
        links_db.add_link(links[i % 4], i % 100, 1)
        if i % 50 == 0:
            for j in range(25):
                links_db.get_link()
