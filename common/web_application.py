import web


class WebApplication(web.application):
        def run(self, address='0.0.0.0', port=8080, *middleware):
            func = self.wsgifunc(*middleware)
            print address
            print port
            return web.httpserver.runsimple(func, (address, port))