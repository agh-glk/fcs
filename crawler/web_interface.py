import web
from crawler import Crawler
from threading import Event
import json

from thread_with_exc import ThreadWithExc

crawler = None
server = None
event = Event()


class index:
    def GET(self):
        return str(crawler.get_state())


class put_links:
    def POST(self):
        _data = json.loads(web.data())
        try:
            _id = _data['id']
            _links = _data['links']
            _server_address = _data['server_address']
            _crawling_policy = _data['crawling_policy']
        except KeyError:
            raise Exception("Invalid request body!")
        crawler.put_into_link_queue([_id, _server_address, _crawling_policy, _links])
        event.set()
        return str(_links) + " crawling in progress."


class stop:
    def POST(self):
        crawler.stop()
        event.set()
        server.kill()
        return "Stop successful"


class kill:
    def POST(self):
        crawler.kill()
        event.set()
        server.kill()
        return "Kill successful"


class Server(ThreadWithExc):

    urls = (
            '/', 'index',
            '/put_links', 'put_links',
            '/kill', 'kill',
            '/stop', 'stop'
        )

    def __init__(self):
        super(Server, self).__init__()
        self.app = web.application(self.__class__.urls, globals())

    def run(self):
        self.app.run()

    def kill(self):
        self.app.stop()
        print "Server stop"
        exit(0)


if __name__ == "__main__":
    event.clear()
    server = Server()
    server.start()
    crawler = Crawler(event)
    crawler.start()
    server.join()
    print "Main thread stop"

