from __future__ import unicode_literals

import wsgiref.headers
import httplib
import io


def make_OK_bytestring():
    response_headers = [('Content-Type', 'text/plain; charset=utf-8')]
    header = wsgiref.headers.Headers(response_headers)
    headerstring = "HTTP/1.1 200 OK\r\n" + str(header)
    return headerstring.encode("utf-8")


def make_ERROR_bytestring(ERR_CODE):
    headerstring = "HTTP/1.1 %i %s\r\n" \
                   % (ERR_CODE, httplib.responses[ERR_CODE])
    return headerstring.encode("utf-8")


def parse_and_respond(request):
    try:
        method, uri, protocol = tuple(request.split())
    except ValueError:
        raise IOError("Bad request")
    if method != "GET":
        raise IOError("Bad method: only GET accepted")
    if protocol != "HTTP/1.1":
        raise IOError("Bad protocol: only HTTP/1.1 allowed")
    try:
        asset = io.open(uri)
        return asset.read()
    except:
        raise IOError("File not found")
