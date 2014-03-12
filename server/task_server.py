import json
import threading
import time
import requests
from linkdb import LinkDB
from contentdb import ContentDB


class status:
    INIT = 0
    STARTING = 1
    RUNNING = 2


class TaskServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.status = status.INIT
        self.link_db = LinkDB()
        self.content_db = ContentDB()
        self.crawlers = []
        self.address = ''

    def assign_task(self, whitelist):
        self.add_links(whitelist)

    def assign_crawlers(self, addresses):
        self.crawlers = addresses

    def assign_address(self, address):
        self.address = address

    def has_crawlers(self):
        return len(self.crawlers) > 0

    def has_address(self):
        return self.address != ''

    def register_to_management(self):
        # TODO: ask management for task definition and crawlers addresses
        whitelist = ["onet.pl", "wp.pl", "facebook.com"]
        crawlers = ["http://address1", "http://address2"]
        self.assign_task(whitelist)
        self.assign_crawlers(crawlers)
        
    def run(self):
        self.status = status.STARTING
        self.register_to_management()
        self.status = status.RUNNING
        while not self.has_address():
            time.sleep(5)
            print 'not running', self.status, self.crawlers, self.address
        token = 0
        while True:
            print 'running'
            links = self.link_db.get_links(5)
            if links:
                r = requests.post(self.crawlers[token] + '/put_links', json.dumps({'task_self': self.address,
                                                                                     'crawling_type': 0,
                                                                                     'links': links}))
                token = (token + 1) % len(self.crawlers)
                print r
            time.sleep(1)

    #TODO: remove
    def links(self):
        return self.link_db.content()

    def feedback(self, regex, rate):
        self.link_db.feedback(regex, rate)

    def add_links(self, links):
        self.link_db.add_links(links)

    def put_data(self, url, links, content):
        self.content_db.add_content(url, links, content)
        self.link_db.add_links(links)

