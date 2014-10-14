"""
code that tests the DoublyLinkedList class defined in doubly_linked_list.py

can be run with py.test
"""
from __future__ import unicode_literals

import pytest  # used for the exception testing

from echo_client import Client
from echo_server import Server
import socket
import threading


@pytest.yield_fixture(scope='function')
def server_running(request):
    """Start the server and have it listening and ready to respond"""
    server = Server()
    t = threading.Thread(target=server.listen_and_respond)
    t.daemon = True
    t.start()
    yield
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
    assert client.send() == "I heard you say: Hi there"
