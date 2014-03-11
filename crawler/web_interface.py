import web
from crawler import Crawler
from threading import Thread
import json

import time
import inspect
import ctypes

crawler = None


class index:
    def GET(self):
        return str(crawler.get_state())


class put_links:
    def POST(self):
        _data = json.loads(web.data())
        _links = _data['links']
        crawler.put_into_link_queue(_links)
        crawler.crawl()
        return str(_links) + " crawling in progress."


class ThreadWithExc(Thread):

    def raise_exc(self, exctype):
        tid = self.ident
        if not inspect.isclass(exctype):
            raise TypeError("Only types can be raised (not instances)")
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("Invalid thread id")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
            raise SystemError("Raise exception failed")


class Server(ThreadWithExc):

    def run(self):
        urls = (
            '/', 'index',
            '/put_links', 'put_links'
        )
        app = web.application(urls, globals())
        app.run()


if __name__ == "__main__":
    crawler = Crawler()
    server = Server()
    server.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.raise_exc(KeyboardInterrupt)
        server.join()
        exit(0)
