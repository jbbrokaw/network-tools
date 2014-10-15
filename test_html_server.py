"""
code that tests the HttpServer class
defined in http_server.py

can be run with py.test
"""
from __future__ import unicode_literals

import pytest  # used for the exception testing

from echo_client import Client
from html_server import HtmlServer
import socket
import threading
import io


@pytest.yield_fixture(scope='session')
def server_running(request):
    """Start the server and have it listening and ready to respond"""
    server = HtmlServer()
    t = threading.Thread(target=server.listen_continuously)
    t.daemon = True
    t.start()
    yield
    server.listening = False
    server.close()


def test_server_init():
    server = HtmlServer()
    assert server._config == (socket.AF_INET,
                              socket.SOCK_STREAM, socket.IPPROTO_IP)


def test_server_multiple_connections(server_running):
    client = Client()
    testfile = io.open("index.html")
    content = testfile.read()
    client.message = "GET index.html HTTP/1.1\r\n"
    response = client.send_and_close()
    assert response == "HTTP/1.1 200 OK\r\n" + \
        "Content-Type: text/plain; charset=utf-8\r\n\r\n" +\
        content

    client.message = "POST index.html HTTP/1.1\r\n"
    response = client.send_and_close()
    assert response == "HTTP/1.1 405 Method Not Allowed\r\n"

    client.message = "GET ind.html HTTP/1.1\r\n"
    response = client.send_and_close()
    assert response == "HTTP/1.1 404 Not Found\r\n"

    client.message = "GET index.html HTTP/2.1\r\n"
    response = client.send_and_close()
    assert response == "HTTP/1.1 505 HTTP Version Not Supported\r\n"

    client.message = "Hi there how are you I am fine nice weather, yeah?"
    response = client.send_and_close()
    assert response == "HTTP/1.1 400 Bad Request\r\n"
