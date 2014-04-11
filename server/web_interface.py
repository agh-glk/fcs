import threading
import sys
import web
import json
from task_server import TaskServer
from common.web_application import WebApplication
import os


server = None


class index:
    def GET(self):
        ret = json.dumps({'status': server.status}) + '\n\n'
        ret += json.dumps({'crawled_links': server.content_db.size()}) + '\n\n'
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
    def GET(self):
        size = int(web.input().size)
        _file_path = server.get_data(size)
        web.header('Content-type', 'text/html')
        web.header('Transfer-Encoding', 'chunked')
        web.header('Content-Disposition', 'attachment; filename=test.txt')
        _crawling_results_file = None
        try:
            _crawling_results_file = open(_file_path, 'rb')
            while True:
                _data = _crawling_results_file.read(1024)
                if not _data:
                    break
                yield _data
        finally:
            _crawling_results_file.close()
            os.remove(_crawling_results_file.name)


class alive:
    def GET(self):
        return 'OK'


class kill:
    def POST(self):
        server.kill()
        return 'OK'


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
            '/get_data', 'get_data',
            '/alive', 'alive',
            '/kill', 'kill'
        )
        self.app = WebApplication(urls, globals())

    def run(self):
        try:
            self.app.run(address=self.address, port=self.port)
        finally:
            server.kill()

    def get_host(self):
        return '%s:%d' % (self.address, self.port)

    def stop(self):
        self.app.stop()
        sys.exit()


# TODO: sys.argv[2] - task id!
if __name__ == '__main__':
    port = int(sys.argv[1])
    task_id = sys.argv[2]
    manager_address = sys.argv[3]
    server = TaskServer(WebServer(port=port), task_id, manager_address)
    server.start()