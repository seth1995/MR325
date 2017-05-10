# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.httpclient
from tornado.escape import json_decode
from tornado.options import define, options
import json
import matplotlib
matplotlib.use('Agg')
import spice

define("port", default=8080, help="run on the given port", type=int)


class SpiceHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):

        print 'post message'
        remote_ip = self.request.remote_ip
        print remote_ip
        print self.request.body_arguments
        print self.request.body
        data = self.request.body_arguments
        try:
            netlist = data['netlist'][0]
        except BaseException:
            result = json.dumps({"result": "0"})
            self.write(result)
            self.finish()
        result = spice.parse(netlist)
        result["result"] = "1"
        result = json.dumps(result)
        self.write(result)
        self.finish()

    def set_default_headers(self):
        # This line is important, tornado won't be able to communicate with
        # front end without this line
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-type', 'application/json;charset=utf-8')
class newSpiceHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):

        print 'post message'
        remote_ip = self.request.remote_ip
        print remote_ip
        print self.request.body_arguments
        print self.request.body
        data = self.request.body_arguments
        try:
            netlist = data['netlist'][0]
        except BaseException:
            result = json.dumps({"result": "0"})
            self.write(result)
            self.finish()
        result = spice.parse_new(netlist)
        result["result"] = "1"
        result = json.dumps(result)
        self.write(result)
        self.finish()

    def set_default_headers(self):
        # This line is important, tornado won't be able to communicate with
        # front end without this line
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-type', 'application/json;charset=utf-8')


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r'/', SpiceHandler),(r'/new', newSpiceHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
