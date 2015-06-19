#-*- coding:utf-8 -*-

import tornado.ioloop
import tornado.httpserver
import handlers,os


ip   = os.environ['OPENSHIFT_PYTHON_IP'] # replace here with your own IP, example 192.168.3.1 or even a localhost
port = int(os.environ['OPENSHIFT_PYTHON_PORT']) # replace here with the port you want to use, example 8000 or 8888

urls = [
    ("/", handlers.RootHandler),
    (r"/upload", handlers.Upload),
    (r"/thanks", handlers.Thanks),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path":r"{0}".format(os.path.join(os.path.dirname(__file__),"static"))}),
]

settings = dict({
    "template_path": os.path.join(os.path.dirname(__file__),"templates"),
    "static_path": os.path.join(os.path.dirname(__file__),"static"),
    "cookie_secret": os.urandom(12),
    "xsrf_cookies": True,
    "debug": False,
    "compress_response": True,
})

application = tornado.web.Application(urls,**settings)


if __name__ == "__main__":
    server = tornado.httpserver.HTTPServer(application)
    server.listen(port, ip)
    tornado.ioloop.IOLoop.instance().start()
