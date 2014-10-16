#!/usr/bin/env python

from __future__ import unicode_literals

import wsgiref.headers
import httplib
import io
import os
import socket
import pathlib


def make_OK_bytestring(content_type):
    response_headers = [('Content-Type', content_type)]
    header = wsgiref.headers.Headers(response_headers)
    headerstring = "HTTP/1.1 200 OK\r\n" + str(header)
    return headerstring.encode("utf-8")


def make_ERROR_bytestring(ERR_CODE):
    headerstring = "HTTP/1.1 %i %s\r\n" \
                   % (ERR_CODE, httplib.responses[ERR_CODE])
    return headerstring.encode("utf-8")


def find_asset_and_type(asset_name):
    asset_name = "webroot/" + asset_name
    print "Attempting to find ", asset_name
    if os.path.isdir(asset_name):
        dirlist = []
        p = pathlib.Path(asset_name)
        for filename in p.iterdir():
            dirlist.append(str(filename))
        data = "<html><body><p>" + "</p><p>".join(dirlist) \
            + "</p></body></html>"
        return data, "html"
    else:
        asset = io.open(asset_name)  # IOError if this fails is handled outside
        asset_type = asset_name.split('.').pop()  # just the end stuff
        # THE ABOVE LINE WILL BREAK if we pass args like "/index.html?user=bob"
        return asset.read(), asset_type


def parse_and_respond(request):
    try:
        command = request.splitlines()[0]
        method, uri, protocol = tuple(command.split())
        asset_name = "." + uri  # Makes it like ./index.html or ./dir
    except ValueError:
        raise IOError("Bad request")

    if method != "GET":
        raise IOError("Bad method: only GET accepted")

    if protocol != "HTTP/1.1":
        raise IOError("Bad protocol: only HTTP/1.1 allowed")

    try:
        return find_asset_and_type(asset_name)
    except:
        raise IOError("File not found")


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
            asset, asset_type = parse_and_respond(received_message)
        except IOError as err:
            if "Bad request" in err.message:
                response = make_ERROR_bytestring(400)
            elif "Bad method" in err.message:
                response = make_ERROR_bytestring(405)  # Return error message
            elif "Bad protocol" in err.message:
                response = make_ERROR_bytestring(505)
            elif "File not found" in err.message:
                response = make_ERROR_bytestring(404)
            else:
                response = make_ERROR_bytestring(500)
                print err
                    # Internal server error: WE SHOULD NEVER GET THIS
        else:
            response = make_OK_bytestring(asset_type) + asset
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
