"""
code that tests the funcitons in http_server.py

can be run with py.test
"""
from __future__ import unicode_literals

import pytest  # used for the exception testing

import http_server as h


def test_make_OK_bytestring():
    assert h.make_OK_bytestring().decode('utf-8') == \
        "HTTP/1.1 200 OK\nContent-Type: text/plain; charset=utf-8\r\n\r\n"
        # Or something like this!? I don't know how to validate this


def test_make_ERROR_bytestring():
    assert h.make_ERROR_bytestring(504) == \
        "HTTP/1.1 504 Gateway Timeout\nContent-Type:" +\
        " text/plain; charset=utf-8\r\n\r\n"


def test_parse_and_respond():
    assert h.parse_and_respond("GET /index.html HTTP/1.1") == "/index.html"
    with pytest.raises(IOError) as err:
        h.parse_and_respond("POST /index.html HTTP/1.1")
        assert "bad method" in err.value
    with pytest.raises(IOError):
        h.parse_and_respond("GET /index.html HTTP/2.0")
        assert "bad protocol" in err.value
