import threading
import sys
import web
import json
from task_server import TaskServer
from common.web_application import WebApplication

server = None


class index:
    def GET(self):
        ret = json.dumps({'status': server.status}) + '\n\n'
        ret += json.dumps({'crawled_links': server.content_db.size()}) + '\n\n'
        ret += json.dumps({'gathered_links': len(server.links())}) + '\n\n'
        ret += json.dumps({'processing_crawlers': server.processing_crawlers}) + '\n\n'
        ret += json.dumps({'idle_crawlers': server.get_idle_crawlers()}) + '\n\n'
        ret += json.dumps(server.package_cache) + '\n\n'
        return ret


class feedback:
    def POST(self):
        data = json.loads(web.data())
        regex = data['regex']
        rate = data['rate']
        server.feedback(regex, rate)
        return 'OK'


class add:
    def POST(self):
        data = json.loads(web.data())
        links = data['links']
        server.add_links(links)
        return 'OK'


class put_data:
    def POST(self):
        data = json.loads(web.data())
        package_id = data['id']
        package_data = data['data']
        server.put_data(package_id, package_data)
        return 'OK'


class crawlers:
    def POST(self):
        data = json.loads(web.data())
        crawlers_addresses = data['addresses']
        server.assign_crawlers(crawlers_addresses)
        return 'OK'


class update:
    def POST(self):
        data = json.loads(web.data())
        server.update(data)
        return 'OK'


class stop:
    def POST(self):
        server.stop()
        return 'OK'


class get_data:
    def POST(self):
        data = server.get_data()
        # TODO: handle Unicode Errors
        return json.dumps(data)


class WebServer(threading.Thread):

    def __init__(self, address='127.0.0.1', port=8800):
        threading.Thread.__init__(self)
        self.address = address
        self.port = port

        urls = (
            '/', 'index',
            '/feedback', 'feedback',
            '/add', 'add',
            '/put_data', 'put_data',
            '/crawlers', 'crawlers',
            '/update', 'update',
            '/stop', 'stop',
            '/get_data', 'get_data'
        )
        self.app = WebApplication(urls, globals())

    def run(self):
        self.app.run(address=self.address, port=self.port)

    def get_host(self):
        return '%s:%d' % (self.address, self.port)

    def stop(self):
        self.app.stop()
        sys.exit()


if __name__ == '__main__':
    port = int(sys.argv[1])
    task_id = sys.argv[2]
    manager_address = sys.argv[3]
    server = TaskServer(WebServer(port=port), task_id, manager_address)
    server.start()