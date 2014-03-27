import web


class WebApplication(web.application):
        def run(self, address='127.0.0.1', port=8080, *middleware):
            func = self.wsgifunc(*middleware)
            return web.httpserver.runsimple(func, (address, port))