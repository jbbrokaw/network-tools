"""
code that tests the Client and Server classes 
defined in echo_client.py and echo_server.py

can be run with py.test
"""
from __future__ import unicode_literals

import pytest  # used for the exception testing

from echo_client import Client
from echo_server import Server
import socket
import threading


@pytest.yield_fixture(scope='session')
def server_running(request):
    """Start the server and have it listening and ready to respond"""
    server = Server()
    t = threading.Thread(target=server.listen_continuously)
    t.daemon = True
    t.start()
    yield
    client = Client("SHUTDOWN")
    client.send_and_close()
    server.close()


def test_server_init():
    server = Server()
    assert server._config == (socket.AF_INET,
                              socket.SOCK_STREAM, socket.IPPROTO_IP)


def test_client_init():
    client = Client("Hi there")
    assert client._config == (socket.AF_INET,
                              socket.SOCK_STREAM, socket.IPPROTO_IP)
    assert client.message == "Hi there"


def test_client_send(server_running):
    client = Client("Hi there")
    assert client.send_and_close() == "I heard you say: Hi there"


def test_server_multiple_connections(server_running):
    client = Client()
    for i in xrange(10):
        client.message = "Test %i" % i
        response = client.send_and_close()
        assert response == "I heard you say: Test %i" % i
