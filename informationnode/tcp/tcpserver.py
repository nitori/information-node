
'''
information-node - an advanced tool for data synchronization
Copyright (C) 2015  Information Node Development Team (see AUTHORS.md)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

import ctypes
import errno
import gnutls.crypto, gnutls.connection
import platform
import socket

if platform.system().lower() == "windows":
    from ctypes import windll
    WSASetLastError = windll.ws2_32.WSASetLastError

def gnutls_init():
    gnutls.crypto.gnutls_global_init()
gnutls_init()
 
class TCPServer(object):
    """ TCP Server which uses epoll and such, and supports GnuTLS. """
    def __init__(self, interface="::0", port=80, tls_cert_path=None,
            tls_key_path=None):
        self.handler = TCPConnectionsHandler()
        self.tls_cert_path = tls_cert_path
        self.bind_interface = interface
        self.bind_port = port
        if tls_cert_path != None:
            self.use_tls = True
            self.tls_cert = X509Certificate(open(tls_cert_path).read())
            self.tls_key = X509PrivateKey(open(tls_key_path).read())
            self.tls_cred = X509Credentials(self.tls_cert, self.tls_key, [],
                [])
        else:
            self.use_tls = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.use_tls:
            self.tls_session = ServerSessionFactory(self.socket,
                self.tls_cred)
            gnutls.crypto.gnutls_transport_set_push_function(
                self.tls_session, self.tls_send)
            gnutls.crypto.gnutls_transport_set_pull_function(
                self.tls_session, self.tls_recv)
            self.tls_session.bind((self.bind_interface, port))
            self.tls_session.listen(100)
            self.handler.add_tls_connection(self.tls_session)
        else:
            self.socket.bind((self.bind_interface, port))
            self.socket.listen(100)
            self.handler.add_plain_connection(self.socket)

class TCPConnectionInfo(object):
    def __init__(self, socket_or_session, use_tls=False):
        self.connection = socket_or_session
        self.use_tls = use_tls

class TCPConnectionsHandler(object):
    def __init__(self):
        self.connections = set()

    def add_plain_connection(self, socket):
        tinfo = TCPConnectionInfo(socket)
        self.connections.add(tinfo)

    def add_tls_connection(self, tls_session):
        tinfo = TCPConnectionInfo(tls_session, use_tls=True)
        self.connections.add(tinfo)

    def tls_send(self, transport_ptr, data, data_len):
        if platform.system().lower() == "windows":
            WSASetLastError(errno.WSAEWOULDBLOCK)
        ctypes.set_errno(errno.EAGAIN)
        return -1

    def tls_recv(self, transport_ptr, data, data_len):
        if platform.system().lower() == "windows":
            WSASetLastError(errno.WSAEWOULDBLOCK)
        ctypes.set_errno(errno.EAGAIN)
        return -1

    

