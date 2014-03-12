import heapq
import re

BEST_PRIORITY = 0
WORST_PRIORITY = 10
START_PRIORITY = 5


class LinkDB:
    def __init__(self):
        self.counter = 0
        self.db = []
        self.links = []
        self.rating = {}

    def add_links(self, links, priority=START_PRIORITY):
        for link in links:
            self.add_link(link, priority)

    def add_link(self, link, default):
        if link in self.links:
            return
        self.links.append(link)
        priority = self.evaluate(link, default)
        heapq.heappush(self.db, (priority, self.counter, link))
        self.counter += 1

    def get_link(self):
        link = heapq.heappop(self.db)[2]
        return link

    def get_links(self, n):
        links = []
        try:
            for i in range(n):
                links.append(self.get_link())
        except IndexError:
            pass
        return links

    #TODO: remove
    def content(self):
        return self.db

    def feedback(self, regex, rate):
        self.rating[regex] = rate
        for i in range(len(self.db)):
            entry = self.db[i]
            self.db[i] = (self.evaluate(entry[2], entry[0]), entry[1], entry[2])
        heapq.heapify(self.db)

    def evaluate(self, link, default):
        priorities = []
        for regex in self.rating:
            if re.match(regex, link):
                priorities.append(self.rating[regex])
        if priorities:
            return sorted(priorities)[-1]  # worst priority
        else:
            return default


