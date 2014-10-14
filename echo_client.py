#!/usr/bin/env python
from __future__ import unicode_literals
import sys
import socket


class Client():
    _config = (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    _buffsize = 4096

    def __init__(self, message=None):
        self.message = message

    def send(self):
        client_socket = socket.socket(*self._config)
        client_socket.connect(('127.0.0.1', 50000))
        client_socket.sendall(self.message)
        client_socket.shutdown(socket.SHUT_WR)
        response = client_socket.recv(32)
        client_socket.close()
        return response


if __name__ == '__main__':
    if len(sys.argv) > 1:
        client = Client(sys.argv[1])
    else:
        client = Client("BOO!")
    print client.send()
