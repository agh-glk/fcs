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
    def __init__(self, web_server):
        threading.Thread.__init__(self)
        self.status = status.INIT
        self.link_db = LinkDB()
        self.content_db = ContentDB()
        self.crawlers = []
        self.web_server = web_server

    def assign_task(self, whitelist):
        self.add_links(whitelist)

    def assign_crawlers(self, addresses):
        self.crawlers = addresses

    def get_address(self):
        return 'http://' + self.web_server.get_host()

    def register_to_management(self):
        # TODO: ask management for task definition and crawlers addresses
        whitelist = ["onet.pl", "wp.pl", "facebook.com"]
        crawlers = ["http://address1", "http://address2"]
        self.assign_task(whitelist)
        self.assign_crawlers(crawlers)

    def run(self):
        self.status = status.STARTING
        self.web_server.start()
        self.register_to_management()
        self.status = status.RUNNING
        while True:
            for crawler in self.crawlers:
                links = self.link_db.get_links(1)
                if links:
                    try:
                        requests.post(crawler + '/put_links', json.dumps({'task_server': self.get_address(),
                                                                'crawling_type': 0, 'links': links}))
                    except Exception as e:
                        print e
            time.sleep(5)

    #TODO: remove
    def links(self):
        return self.link_db.content()

    def contents(self):
        return self.content_db.content()

    def feedback(self, regex, rate):
        self.link_db.feedback(regex, rate)

    def add_links(self, links):
        self.link_db.add_links(links)

    def put_data(self, url, links, content):
        self.content_db.add_content(url, links, content)
        self.link_db.add_links(links)