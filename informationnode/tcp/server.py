
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
import informationnode.gnutls as gnutls
import platform
from selectors import DefaultSelector
import socket

if platform.system().lower() == "windows":
    from ctypes import windll
    WSASetLastError = windll.ws2_32.WSASetLastError

gnutls.gnutls_global_init()
 
class TCPServer(object):
    """ TCP Server which uses epoll (or similar) and supports GnuTLS.
        A callback returns new connections as sockets. Note on threading: this
        callback is issued from the same thread that calls
        tcp_server.process() during the execution of that function.

        Important: the returned sockets are almost like python standard
        sockets, however:

        - The sockets provide an alternative way of reading through
          socket.set_receive_callback(func) where you can provide a custom
          handler function.

          This alternative api is highly advised instead of calling
          socket.recv(amount) directly for better performance and easier use.
          Your provided handler function will be passed the socket and the
          received byte array as parameters on each call.

          Note on threading: those callbacks will happen on the same thread
          where you called tcp_server.process() on the owning server.
    """
    def __init__(self, interface="::0", port=80, tls_cert_path=None,
            tls_key_path=None, check_cert_callback=None,
            new_client_callback=None):
        self.handler = _TCPConnectionsHandler()
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
            gnutls.gnutls_transport_set_push_function(
                self.tls_session, self.tls_send)
            gnutls.gnutls_transport_set_pull_function(
                self.tls_session, self.tls_recv)
            self.tls_session.bind((self.bind_interface, port))
            self.tls_session.listen(100)
            self.handler.add_tls_connection(self.socket, self.tls_session,
                server=True)
        else:
            self.socket.bind((self.bind_interface, port))
            self.socket.listen(100)
            self.handler.add_plain_connection(self.socket, server=True)

class TCPWrappedSocket(object):
    def __init__(self, tcp_handler, socket, tls_session=None, uses_tls=False,
            server_and_auto_accept=False):
        self.connection = socket_or_session
        self.uses_tls = use_tls
        self.tls_session = tls_session
        self.server_and_auto_accept = server_and_auto_accept

    def set_receive_callback(self, callback):
        self.receive_callback = callback

    def send(self, data):
        return -1

    def recv(self, data):
        if platform.system().lower() == "windows":
            WSASetLastError(errno.WSAEWOULDBLOCK)
        ctypes.set_errno(errno.EAGAIN)
        return -1

    def write(self, data):
        return send(self, data)

    def read(self, amount):
        return self.recv(amount)

    def set_receive_callback(self, callback):
        self.receive_callback = callback


class _TCPConnectionsHandler(object):
    def __init__(self):
        self.connections = dict()
        self.recv_selector = DefaultSelector()
        self.send_selector = DefaultSelector()

    def add_plain_connection(self, socket, receive_callback, server=False):
        tinfo = TCPWrappedSocket(self, socket, server_and_auto_accept=server)
        self.connections[socket] = tinfo

    def add_tls_connection(self, socket, tls_session, receive_callback,
            server=False):
        tinfo = TCPWrappedSocket(self, socket, tls_session, uses_tls=True,
            server_and_auto_accept=server)
        self.connections.add[tls_session] = tinfo
        self.connections.add[socket] = tinfo
        gnutls.gnutls_transport_set_push_function(
            tls_session, self._tls_custom_io_send)
        gnutls.gnutls_transport_set_pull_function(
            self.tls_session, self._tls_custom_io_recv)

    def remove_connection_by_socket(self, socket):
        tinfo = self.connections[socket]
        if tinfo.uses_tls:
            tls_session = tinfo.tls_session
            del(self.connections[tls_session])
        del(self.connections[socket])
        del(tinfo)

    def remove_connection_by_tls_session(self, tls_session):
        tinfo = self.connections[tls_session]
        del(self.connections[tinfo.socket])
        del(self.connections[tls_session])
        del(tinfo)

    def _tls_custom_io_send(self, transport_ptr, data, data_len):
        if platform.system().lower() == "windows":
            WSASetLastError(errno.WSAEWOULDBLOCK)
        ctypes.set_errno(errno.EAGAIN)
        return -1

    def _tls_custom_io_recv(self, transport_ptr, data, data_len):
        if platform.system().lower() == "windows":
            WSASetLastError(errno.WSAEWOULDBLOCK)
        ctypes.set_errno(errno.EAGAIN)
        return -1

    

