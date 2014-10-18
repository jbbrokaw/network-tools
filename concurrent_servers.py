#!/usr/bin/env python
from __future__ import unicode_literals

from gevent.server import StreamServer

from http_server import parse_and_respond, make_ERROR_bytestring,\
    make_OK_bytestring
from http_server import HttpServer


def generate_response(conn, addr):
    # Mostly identical to HttpServer.listen_and_respond,
    # but has different arguments and doesn't listen
    received_message = conn.recv(HttpServer._buffsize)
    print "Parsing message from", addr
    print received_message
    try:
        asset, asset_type, asset_length = \
            parse_and_respond(received_message)
    except IOError as err:
        if "Bad request" in err.message:
            response = make_ERROR_bytestring(400)
        elif "Bad method" in err.message:
            response = make_ERROR_bytestring(405)
        elif "Bad protocol" in err.message:
            response = make_ERROR_bytestring(505)
        elif "File not found" in err.message:
            response = make_ERROR_bytestring(404)
        else:
            response = make_ERROR_bytestring(500)
            print err
                # Internal server error: WE SHOULD NEVER GET THIS
    except IndexError:  # This raises from splitlinesif we get a blank
        response = make_ERROR_bytestring(400)
    else:
        response = make_OK_bytestring(asset_type, asset_length) + asset
    conn.sendall(response)
    conn.close()


class ConcurrentServer(StreamServer):
    def __init__(self):
        StreamServer.__init__(self, ('127.0.0.1', 8888), generate_response)

    def runnicely(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            self.stop()
            print "Exiting Gracefully"


if __name__ == '__main__':
    server = ConcurrentServer()
    server.runnicely()
