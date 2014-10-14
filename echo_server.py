#!/usr/bin/env python
from __future__ import unicode_literals

import socket


class Server():
    _config = (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    _buffsize = 4096
    server_socket = socket.socket(*_config)
    server_socket.bind(('127.0.0.1', 50000))

    def listen_and_respond(self):
        self.server_socket.listen(1)  # Stops here
        conn, addr = self.server_socket.accept()
        received_message = conn.recv(self._buffsize)
        print "Echoing message from", addr
        response = "I heard you say: %s" % received_message
        conn.sendall(response)

    def close(self):
        self.server_socket.close()

if __name__ == '__main__':
    server = Server()
    server.listen_and_respond()  # Maybe put this in a loop
    server.close()
