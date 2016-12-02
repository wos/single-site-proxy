import http.server
import socketserver

import socket
import socks
import sys
import configparser

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


c = configparser.ConfigParser()
c.read('proxy.conf')

PORT = c.getint('proxy', 'port')
baseUrl = c.get('proxy', 'baseurl')
torUrl = c.get('proxy', 'torurl')

socket_connected = False


def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock


def connect_to_socket():
    global socket_connected
    if not socket_connected:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
        socket.socket = socks.socksocket
        socket.create_connection = create_connection

        socket_connected = True


def socket_disconnect():
    global socket_connected
    if socket_connected:
        # socket.socket =
        socket_connected = False


class ProxyHandler (http.server.BaseHTTPRequestHandler):
    __version__ = '0.0.1'
    server_version = "ProxyHTTP/" + __version__

    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_GET(s):
        """Respond to a GET request."""
        connect_to_socket()
        try:
            request = urllib2.urlopen(torUrl + s.path)
            data = request.read()
            s.send_response(200)
            for header in request.info().as_string().split('\n'):
                hsplit = header.split(':')
                if (len(hsplit) == 2):
                    s.send_header(hsplit[0].strip(), hsplit[1].strip())

            s.end_headers()

            s.wfile.write(data)
        except:
            sys.exit(0)


Handler = ProxyHandler
httpd = socketserver.TCPServer(("", PORT), Handler)
try:
    print("serving at port", PORT)
    httpd.serve_forever()
except:
    sys.exit(0)
