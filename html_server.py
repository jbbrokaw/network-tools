#!/usr/bin/env python
from __future__ import unicode_literals

import socket
import http_server as h


class HtmlServer():
    _config = (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    _buffsize = 4096
    server_socket = socket.socket(*_config)
    server_socket.bind(('127.0.0.1', 50000))

    def __init__(self):
        self.listening = False

    def listen_and_respond(self):
        self.server_socket.listen(1)  # Stops here
        conn, addr = self.server_socket.accept()
        received_message = conn.recv(self._buffsize)
        print "Parsing message from", addr
        print received_message
        try:
            uri = h.parse_and_respond(received_message)
        except IOError as err:
            if "Bad request" in err.message:
                response = h.make_ERROR_bytestring(400)
            elif "Bad method" in err.message:
                response = h.make_ERROR_bytestring(405)  # Return error message
            elif "Bad protocol" in err.message:
                response = h.make_ERROR_bytestring(505)
            elif "File not found" in err.message:
                response = h.make_ERROR_bytestring(404)
            else:
                response = h.make_ERROR_bytestring(500)
                print err
                    # Internal server error: WE SHOULD NEVER GET THIS
        else:
            response = h.make_OK_bytestring() + uri
        conn.sendall(response)

    def close(self):
        self.server_socket.close()

    def listen_continuously(self):
        self.listening = True
        while self.listening:
            self.listen_and_respond()

if __name__ == '__main__':
    server = HtmlServer()
    try:
        server.listen_continuously()  # Maybe put this in a loop
    except KeyboardInterrupt:
        print "Exiting gracefully"
    finally:  # Still do this if there's a keyboard interrupt or something
        server.close()
