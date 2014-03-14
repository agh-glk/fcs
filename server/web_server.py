import threading
import sys
import web
import json
from task_server import TaskServer

server = None


class index:
    def GET(self):
        ret = json.dumps({'status': server.status}) + '\n\n'
        ret += json.dumps(server.links()) + '\n\n'
        ret += json.dumps(server.contents()) + '\n\n'
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
        for entry in data['data']:
            url = entry['url']
            links = entry['links']
            content = entry['content']

            server.put_data(package_id, url, links, content)
        return 'OK'


class crawlers:
    def POST(self):
        data = json.loads(web.data())
        crawlers_addresses = data['addresses']
        server.assign_crawlers(crawlers_addresses)
        return 'OK'


class pause:
    def POST(self):
        server.pause()
        return 'OK'


class resume:
    def POST(self):
        server.resume()
        return 'OK'


class stop:
    def POST(self):
        server.stop()
        return 'OK'


class WebServer(threading.Thread):
    def __init__(self, address='0.0.0.0', port=8080):
        threading.Thread.__init__(self)
        self.address = address
        self.port = port

    def run(self):
        urls = (
            '/', 'index',
            '/feedback', 'feedback',
            '/add', 'add',
            '/put_data', 'put_data',
            '/crawlers', 'crawlers',
            '/stop', 'stop',
            '/pause', 'pause',
            '/resume', 'resume'
        )
        app = WebServer.Application(urls, globals())
        app.run(address=self.address, port=self.port)

    def get_host(self):
        return '%s:%d' % (self.address, self.port)

    class Application(web.application):
        def run(self, address='0.0.0.0', port=8080, *middleware):
            func = self.wsgifunc(*middleware)
            return web.httpserver.runsimple(func, (address, port))


if __name__ == '__main__':
    server = TaskServer(WebServer(port=8888))
    server.start()