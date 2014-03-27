import heapq
import re
import threading
import bsddb
from key_policy_module import SimpleKeyPolicyModule
import datetime

BEST_PRIORITY = 0
WORST_PRIORITY = 10
START_PRIORITY = 5


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


class SimpleLinkDB(BaseLinkDB):
    def __init__(self):
        self.lock = threading.Lock()
        self.counter = 0
        self.db = []
        self.links = set()
        self.rating = {}

    def add_links(self, links, default_priority=START_PRIORITY, force=False):
        self.lock.acquire()
        for link in links:
            self._add_link(link, default_priority, force)
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

    def __init__(self, base_name, policy_module):
        self.policy_module = policy_module

        self.found_links = bsddb.db.DB()
        self.found_links.open("Found_links", "found_links", bsddb.db.DB_BTREE, bsddb.db.DB_CREATE)

        self.priority_queue = bsddb.db.DB()
        self.priority_queue.set_bt_compare(policy_module.comparison_function)
        self.priority_queue.open("priority_db", "priority_db", bsddb.db.DB_BTREE, bsddb.db.DB_CREATE | bsddb.db.DB_DIRTY_READ)

    def is_in_base(self, link):
        return self.found_links.exists(link)

    def add_link(self, link, priority, depth):
        self.found_links.put(link, ";".join([str(priority), "", str(depth)]))
        _key = self.policy_module.generate_key(link, priority)
        self.priority_queue.put(_key, link)

    def get_link(self):
        _cursor = self.priority_queue.cursor()
        _link = _cursor.first()
        if _link is not None:
            _cursor.delete()
            _cursor.close()
            return _link[1]
        return _link

    def set_as_fetched(self, link):
        _data = self.found_links.get(link).split(';')
        _data[1] = str(datetime.datetime.now())
        self.found_links.put(link, ";".join(_data))

    def feedback(self, link, rate):
        raise NotImplementedError

    def get_details(self, link):
        return self.found_links.get(link).split(';')

    def close(self):
        self.found_links.close()
        self.priority_queue.close()

    def _print_db(self, data_base):
        cursor = data_base.cursor()
        rec = cursor.first()
        print '--------------'
        while rec:
                print rec
                rec = cursor.next()
        print '=============='
        cursor.close()

    def _print(self):
        self._print_db(self.priority_queue)
        self._print_db(self.found_links)


if __name__ == '__main__':

    links_db = BerkeleyBTreeLinkDB("db_name", SimpleKeyPolicyModule)
    _link = "www.zzz.com"
    links_db.add_link(_link, 1, 1)
    #links_db._print()
    links_db.feedback(_link, 5)
    #links_db._print()
    _details = links_db.get_details(_link)
    print _details



