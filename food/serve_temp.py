#!/usr/bin/env python
import SimpleHTTPServer


class RefreshingRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Refresh", "1")
        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)


if __name__ == '__main__':
    SimpleHTTPServer.test(HandlerClass=RefreshingRequestHandler)
