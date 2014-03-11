from linkdb import LinkDB
from contentdb import ContentDB
import status
import threading
import time
import requests
import json


class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.status = status.STARTING
        self.link_db = LinkDB()
        self.content_db = ContentDB()
        self.crawlers = []
        self.address = ''

    def assign_task(self, whitelist):
        self.link_db.add_links(whitelist)
        self.status = status.READY

    def assign_crawlers(self, addresses):
        self.crawlers.extend(addresses)

    def assign_address(self, address):
        self.address = address

    def has_crawlers(self):
        return len(self.crawlers) == 0

    def run(self):
        while (self.status != status.READY) or (not self.has_crawlers()) or (self.address == ''):
            time.sleep(1)
            print 'not running', self.status, self.crawlers, self.address
        token = 0
        while True:
            print 'running'
            links = self.link_db.get_links(5)
            if links:
                r = requests.post(self.crawlers[token] + '/put_links', json.dumps({'task_server': self.address,
                                                                'crawling_type': 0, 'links': links}))
                token = (token + 1) % len(self.crawlers)
                print r
            time.sleep(1)

    #TODO: remove
    def links(self):
        return self.link_db.content()

    def feedback(self, regex, rate):
        self.link_db.feedback(regex, rate)

    def add(self, links):
        self.link_db.add_links(links)

    def put_data(self, url, links, content):
        self.content_db.add_content(url, links, content)
        self.link_db.add_links(links)

