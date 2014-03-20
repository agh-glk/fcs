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
    def __init__(self, address='0.0.0.0', port=8800):
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
        app = WebApplication(urls, globals())
        app.run(address=self.address, port=self.port)

    def get_host(self):
        return '%s:%d' % (self.address, self.port)

    def stop(self):
        web.httpserver.server.stop()


# TODO: sys.argv[2] - task id!
if __name__ == '__main__':
    port = int(sys.argv[1])
    task_id = sys.argv[2]
    manager_address = sys.argv[3]
    server = TaskServer(WebServer(port=port), task_id, manager_address)
    server.start()