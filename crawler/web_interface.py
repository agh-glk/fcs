import sys
import web
from crawler import Crawler
from threading import Event
import json
import sys

from thread_with_exc import ThreadWithExc
from common.web_application import WebApplication

crawler = None
server = None
event = Event()


class index:
    def GET(self):
        return str(str(crawler.get_state()) + '\n\n' + json.dumps(crawler.get_stats(60)))


class put_links:
    def POST(self):
        _data = json.loads(web.data())
        try:
            _id = _data['id']
            _links = _data['links']
            _server_address = _data['server_address']
            _mime_type = _data['crawling_type']
        except KeyError:
            raise Exception("Invalid request body!")
        crawler.put_into_link_queue([_id, _server_address, _mime_type, _links])
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


class alive:
    def GET(self):
        return 'OK'


class stats:
    def POST(self):
        data = json.loads(web.data())
        seconds = int(data['seconds'])
        return json.dumps(crawler.get_stats(seconds))


class Server(ThreadWithExc):

    urls = (
            '/', 'index',
            '/put_links', 'put_links',
            '/kill', 'kill',
            '/stop', 'stop',
            '/alive', 'alive',
            '/stats', 'stats'
        )

    def __init__(self, port=8080, address='0.0.0.0'):
        super(Server, self).__init__()
        self.app = WebApplication(self.__class__.urls, globals())
        self.port = port
        self.address = address

    def run(self):
        try:
            self.app.run(port=self.port, address=self.address)
        finally:
            crawler.stop()
            event.set()

    def kill(self):
        self.app.stop()
        print "Server stop"
        exit(0)


if __name__ == "__main__":
    #TODO : przerobic pobieranie parametrow
    _port = 8080
    _address = '0.0.0.0'
    if len(sys.argv) > 3:
        _address = sys.argv[3]
    if len(sys.argv) > 1:
        _port = int(sys.argv[1])
    event.clear()
    server = Server(_port, _address)
    server.start()
    manager_address = sys.argv[2]
    crawler = Crawler(server, event, _port, manager_address)
    crawler.start()
    server.join()
    print "Main thread stop"

