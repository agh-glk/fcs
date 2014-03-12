import threading
import sys
import web
import json
from task_server import TaskServer

server = None


class index:
    def GET(self):
        return json.dumps({'status': server.status})


class task:
    def POST(self):
        data = json.loads(web.data())
        whitelist = data['whitelist']
        server.assign_task(whitelist)
        return 'OK'


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


class linkdb:
    def GET(self):
        return json.dumps(server.links())


class put_data:
    def POST(self):
        data = json.loads(web.data())
        for entry in data:
            url = entry['url']
            links = entry['links']
            content = entry['content']
            server.put_data(url, links, content)
        return 'OK'


class crawlers:
    def POST(self):
        data = json.loads(web.data())
        addresses = data['addresses']
        server.assign_crawlers(addresses)
        return 'OK'


class WebServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global server
        server = TaskServer()
        server.assign_address('http://0.0.0.0:' + sys.argv[1] + '/')
        server.start()

    def run(self):
        urls = (
            '/', 'index',
            '/task', 'task',
            '/feedback', 'feedback',
            '/add', 'add',
            '/links', 'linkdb',
            '/put_data', 'put_data',
            '/crawlers', 'crawlers'
        )
        app = web.application(urls, globals())
        app.run()

if __name__ == '__main__':
    WebServer().start()