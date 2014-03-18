import heapq
import re
import threading

BEST_PRIORITY = 0
WORST_PRIORITY = 10
START_PRIORITY = 5


class LinkDB:
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



