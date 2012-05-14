from ws4py.client.threadedclient import WebSocketClient

class EchoClient(WebSocketClient):
    def opened(self):
        print "Connected to collective..."

    def closed(self, code, reason=None):
        print code, reason

    def received_message(self, m):
        #self.close()
        pass

