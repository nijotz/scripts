#!/usr/bin/env python

import sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn


class ThreadingServer(ThreadingMixIn, HTTPServer):
    pass


class InfiniteGarbage(BaseHTTPRequestHandler):

    def _garbage(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        garbage = 'HUE HUE HUE '
        while True:
            self.wfile.write(garbage)

    def do_GET(self):
        self._garbage()

    def do_POST(self):
        self._garbage()

    def do_HEAD(self):
        self._garbage()

if __name__ == '__main__':

    port = 8080
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])

    gahbage = ThreadingServer(('', port), InfiniteGarbage)

    try:
        gahbage.serve_forever()
    finally:
        gahbage.socket.close()
