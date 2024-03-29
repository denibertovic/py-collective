# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()

import argparse
import random
import os

import gevent
import gevent.pywsgi

from ws4py.server.geventserver import UpgradableWSGIHandler
from ws4py.server.wsgi.middleware import WebSocketUpgradeMiddleware
from ws4py.websocket import EchoWebSocket

class BroadcastWebSocket(EchoWebSocket):
    def received_message(self, m):
        # self.clients is set from within the server
        # and holds the list of all connected servers
        # we can dispatch to
        for client in self.clients:
            client.send(m)

    def closed(self, code, reason="A harvester disconnected without a proper explanation."):
        if self in self.clients:
            self.clients.remove(self)
            try:
                for client in self.clients:
                    client.send(reason)
            finally:
                self.clients = None
                delattr(self, 'clients')

class EchoWebSocketServer(gevent.pywsgi.WSGIServer):
    handler_class = UpgradableWSGIHandler
    
    def __init__(self, host, port):
        gevent.pywsgi.WSGIServer.__init__(self, (host, port))
        
        self.host = host
        self.port = port

        self.application = self
        
        # let's use wrap the websocket handler with
        # a middleware that'll perform the websocket
        # handshake
        self.ws = WebSocketUpgradeMiddleware(app=self.ws_app,
                                             websocket_class=BroadcastWebSocket)

        # keep track of connected websocket clients
        # so that we can brodcasts messages sent by one
        # to all of them. Aren't we cool?
        self.clients = []

    def __call__(self, environ, start_response):
        """
        Good ol' WSGI application.
        """
        if environ['PATH_INFO'] == '/favicon.ico':
            return self.favicon(environ, start_response)
        
        if environ['PATH_INFO'] == '/ws':
            return self.ws(environ, start_response)
        
        if environ['PATH_INFO'].startswith('/js'):
            return self.static(environ, start_response)
        
        return self.webapp(environ, start_response)

    def ws_app(self, websocket):
        websocket.clients = self.clients
        self.clients.append(websocket)
        g = gevent.spawn(websocket.run)
        g.join()

    def favicon(self, environ, start_response):
        """
        Don't care about favicon, let's send nothing.
        """
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return ""

    def static(self, environ, start_response):
        """
        Not the sexiest static handler but does the job.
        """
        path = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                             './static/%s' % environ['PATH_INFO']))
        if not os.path.exists(path):
            status = '404 Not Found'
            headers = [('Content-type', 'text/plain')]
            return ""
        
        status = '200 OK'
        headers = [('Content-type', 'text/javascript')]
        
        start_response(status, headers)
        
        return file(path).read()
        
    def webapp(self, environ, start_response):
        """
        Our main webapp that'll display the logs
        """
        status = '200 OK'
        headers = [('Content-type', 'text/html')]

        start_response(status, headers)

        return """<html>
        <head>
          <script type='application/javascript' src='js/jquery-1.6.2.min.js'></script>
          <script type='application/javascript'>
            $(document).ready(function() {

              websocket = 'ws://%(host)s:%(port)s/ws';
              if (window.WebSocket) {
                ws = new WebSocket(websocket);
              }
              else if (window.MozWebSocket) {
                ws = MozWebSocket(websocket);
              }
              else {
                console.log('WebSocket Not Supported');
                return;
              }

              ws.onmessage = function (evt) {
                 $('#logs').append('<p>' + evt.data + '</p>');
              };
              /*ws.onopen = function() {
                 ws.send("client registered");
              };*/
              ws.onclose = function(evt) {
                 $('#logs').append('<p>Connection closed by server: ' + evt.code + ' ::: ' + evt.reason + '</p>');  
              };

            });
          </script>
        </head>
        <body>
          <div id='logs'></div>
        </body>
        </html>
        """ % {'host': self.host,
               'port': self.port}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Py-Collective Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=8080, type=int)
    args = parser.parse_args()

    server = EchoWebSocketServer(args.host, args.port)
    server.serve_forever()
    
