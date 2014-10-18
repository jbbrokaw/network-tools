"""
Code that tests the funcitons in http_server.py

can be run with py.test
"""

from __future__ import unicode_literals

# import pytest  # used for the exception testing

import io
from concurrent_servers import ConcurrentServer
import gevent.socket as socket  # Makes sockets nonblocking
import gevent  # Not at all friendly with threading, so
               # had to revise testing procedures
import time


def test_concurrent_server():
    testfile = io.open("webroot/sample.txt")
    content = testfile.read()
    server = ConcurrentServer()

    def clientslow():
        start = time.time()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM,
                                      socket.IPPROTO_IP)
        client_socket.connect(('127.0.0.1', 8888))
        gevent.sleep(1)  # demonstrates it's not closing the connection
        return "Connected and didn't send anything", time.time() - start

    def clientnorm(message):
        start = time.time()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM,
                                      socket.IPPROTO_IP)
        client_socket.connect(('127.0.0.1', 8888))
        client_socket.sendall(message)
        client_socket.shutdown(socket.SHUT_WR)
        response = client_socket.recv(4096)
        client_socket.close()
        server.stop()  # This stops the serverthread
        return response, time.time() - start

    serverthread = gevent.spawn(server.serve_forever)
    client1thread = gevent.spawn(clientslow)
    client2thread = gevent.spawn(clientnorm, "GET /sample.txt HTTP/1.1\r\n")

    serverthread.start()
    client1thread.start()
    gevent.sleep(0.1)  # Let the slow thread get a connection, but not exit
    client2thread.start()

    client2thread.join()
    client1thread.join()
    serverthread.join()
    #These will hang if anything is still waiting

    response, elapsed = client2thread.get()
    assert response == "HTTP/1.1 200 OK\r\n" + \
        "Content-Type: text/plain\r\n" + \
        "Content-Length: 96\r\n\r\n" +\
        content
    assert elapsed < 1  # Faster than the sleeping thread
    response, elapsed = client1thread.get()
    assert response == "Connected and didn't send anything"
    assert elapsed > 1
