"""
code that tests the funcitons in http_server.py

can be run with py.test
"""
from __future__ import unicode_literals

import pytest  # used for the exception testing

import http_server as h
import io
from echo_client import Client
from http_server import HttpServer
import threading
import urllib2


@pytest.yield_fixture(scope='session')
def server_running(request):
    """Start the server and have it listening and ready to respond"""
    server = HttpServer()
    t = threading.Thread(target=server.listen_continuously)
    t.daemon = True
    t.start()
    yield
    server.listening = False
    server.close()


def test_make_OK_bytestring():
    assert h.make_OK_bytestring("text/plain", 48).decode('utf-8') == \
        "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n" + \
        "Content-Length: 48\r\n\r\n"


def test_make_ERROR_bytestring():
    assert h.make_ERROR_bytestring(504) == \
        "HTTP/1.1 504 Gateway Timeout\r\n"


def test_parse_and_respond():
    testfile = io.open("webroot/sample.txt")
    content = testfile.read()
    returned_content, returned_type, returned_length = \
        h.parse_and_respond("GET /sample.txt HTTP/1.1")
    assert content == returned_content
    assert returned_type == "text/plain"
    assert returned_length == str(len(content))

    with pytest.raises(IOError) as err:
        h.parse_and_respond("POST /index.html HTTP/1.1")
        assert "bad method" in err.value
    with pytest.raises(IOError):
        h.parse_and_respond("GET /index.html HTTP/2.0")
        assert "bad protocol" in err.value


def test_server_multiple_connections(server_running):
    client = Client()
    testfile = io.open("webroot/sample.txt")
    content = testfile.read()
    client.message = "GET /sample.txt HTTP/1.1\r\n"
    response = client.send_and_close()
    assert response == "HTTP/1.1 200 OK\r\n" + \
        "Content-Type: text/plain\r\n" + \
        "Content-Length: 96\r\n\r\n" +\
        content

    # The length above is python's idea; this might be inaccurate????

    client.message = "POST /sample.txt HTTP/1.1\r\n"
    response = client.send_and_close()
    assert response == "HTTP/1.1 405 Method Not Allowed\r\n"

    client.message = "GET /ind.html HTTP/1.1\r\n"
    response = client.send_and_close()
    assert response == "HTTP/1.1 404 Not Found\r\n"

    client.message = "GET /sample.txt HTTP/2.1\r\n"
    response = client.send_and_close()
    assert response == "HTTP/1.1 505 HTTP Version Not Supported\r\n"

    client.message = "Hi there how are you I am fine nice weather, yeah?"
    response = client.send_and_close()
    assert response == "HTTP/1.1 400 Bad Request\r\n"

    client.message = "GET /images HTTP/1.1\r\n"
    response = client.send_and_close()
    lines = response.splitlines()
    assert lines[0] == "HTTP/1.1 200 OK"
    assert lines[1] == "Content-Type: text/html"
    assert lines[2] == "Content-Length: " + str(len(lines[4]))

    client.message = "GET /images/sample_1.png HTTP/1.1\r\n"
    response = client.send_and_close()
    lines = response.splitlines()
    asset = \
        urllib2.urlopen("file:///Users/jbbrokaw/repositories/network-tools/" +
                        "webroot/images/sample_1.png")
    assert lines[0] == "HTTP/1.1 200 OK"
    assert lines[1] == "Content-Type: image/png"
    assert lines[2] == "Content-Length: " + asset.headers["Content-Length"]
