import tornado.ioloop
import tornado.web
import tornado.websocket
from stellarnetwork_test import *

import pprint
pp = pprint.PrettyPrinter(indent=4)

s = StellarNetwork()

def send_network_update():
    s.update_all()
    s.update_all_statistics()
    agree = s.get_network_json(s.agree_graph)
    disagree = s.get_network_json(s.disagree_graph)
    missing = s.get_network_json(s.missing_graph)
    fail_with = s.get_network_json(s.fail_with_graph)
    stats = s.get_all_statistics()
    update = {'agree': agree, 'disagree': disagree, 'missing': missing, 'fail_with': fail_with, 'stats': stats['agree']}
    [ cc.write_message(update) for cc in UpdateWSHandler.connections ]
    #pp.pprint(update)

class UpdateWSHandler(tornado.websocket.WebSocketHandler):
    connections = set([])

    def open(self):
        print("WS Opened");
        UpdateWSHandler.connections.add(self)
        self.on_message("Connected")

    def on_message(self,message):
        self.write_message("Something")

    def on_close(self):
        print("WS Closed")
        UpdateWSHandler.connections.remove(self)



settings = {'debug': True}
port = 1011

handlers = [(r'/update/ws', UpdateWSHandler),
        (r'/(.*)', tornado.web.StaticFileHandler, {'path': '/home/sobolosrios/quorum_view', "default_filename": "index_test.html"}),
        (r'/js/*', tornado.web.StaticFileHandler, {'path': '/home/sobolosrios/quorum_view/js'})]  


main_loop = tornado.ioloop.IOLoop.instance()
updater = tornado.ioloop.PeriodicCallback(send_network_update, 5000, io_loop=main_loop)  # Update every 5 seconds
updater.start()
application = tornado.web.Application(handlers, **settings)
application.listen(port)
main_loop.start()


