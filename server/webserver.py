import web
import json
import sys
from server import Server

server = Server()


class status:
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
        server.add(links)
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


urls = (
    '/', 'status',
    '/task', 'task',
    '/feedback', 'feedback',
    '/add', 'add',
    '/links', 'linkdb',
    '/put_data', 'put_data',
    '/crawlers', 'crawlers'
)

if __name__ == '__main__':
    server.start()
    server.assign_address('http://0.0.0.0:' + sys.argv[1] + '/')
    app = web.application(urls, globals())
    app.run()