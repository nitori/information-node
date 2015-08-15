
'''
information-node - an advanced tool for data synchronization
Copyright (C) 2015  information-node Development Team (see AUTHORS.md)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import json
import logging
import platform
import queue
import signal
import threading
import time

class FileSocketApiClientHandler(threading.Thread):
    def __init__(self, client):
        self.daemon = daemon
        self.client = client
        self.socket = client.socket
        self.internal_api_queue = daemon.internal_api_queue

    def process_msg(self, msg):
        """ Process an API msg that was received. """
        logging.debug("received msg from: " + str(self.client.addr))
        logging.debug("msg contents: " + str(msg))

    def run(self):
        try:
            recv_buf = b""
            while True:
                # get message size:
                msg_size = ""
                while len(msg_size) < 4:
                    msg_size += self.socket.recv(4 - len(msg_size))
                msg_size = struct.unpack("!i", msg_size)

                # get message:
                msg = ""
                while len(msg) < msg_size:
                    msg += self.socket.recv(msg_size - len(msg))
                
                # process message:
                try:
                    msg = json.loads(msg)
                    self.process_msg(msg)
                except ValueError:
                    self.socket.close()
                    self.client.socket = None
                    return
        except Exception as e:
            logging.error("Error in FileSocketApiClientHandler.run: " +\
                str(e))
            self.socket.close()
            self.client.socket = None

class FileSocketApiClient(object):
    def __init__(self, daemon, socket, address):
        self.address = address
        self.socket = socket
        self.client_thread = FileSocketApiClientHandler(daemon, socket)
        self.client_thread.start()
    
    def terminated(self):
        if self.socket == None:
            return True
        return False

class Daemon(object):
    def __init__(self):
        self.api_processor_terminated = False
        self.terminate = False
        if platform.system().lower() != "windows":
            signal.signal(signal.SIGTERM, self.sigterm_handler)
            signal.signal(signal.SIGHUP, self.sighup_handler)

    def sigterm_handler(self, signal, unused_info):
        """ SIGTERM handler which will initiate shutdown. """
        self.terminate = True

    def sighup_handler(self, signal, unused_info):
        """ SIGHUP handler. Usually this is used for asking a daemon to reload
            configurations, but we don't offer sucha thing. Therefore, we just
            do nothing here.
         """
        pass

    def internal_api_processor(self):
        """ Internal api processor thread. This thread does the actual I/O
            work on disk.
        """
        while not self.terminate:
            try:
                next_msg = self.internal_api_queue.get(timeout=500)
            except queue.Empty:
                continue
            logging.debug("got internal api message: " + str(next_msg))
            try:
                if msg["action"] == "":
                    pass
            except Exception as e:
                logging.error("Error in Daemon.internal_api_processor: " +\
                    str(e))
        self.api_processor_terminated = True

    def api_socket_processor(self):
        clients = {}
        while True:
            # add new client(s):
            c, addr = s.accept()
            clients[c] = FileSocketApiclient(c, addr)
            
            # throw away clients that have been terminated:
            remove_clients = []
            for client_k in clients:
                if clients[client_k].terminated():
                    remove_clients.append(client_k)
            for client_k in remove_clients:
                del(clients[client_k])

    def run(self, api_socket):
        """ Run the data server which handles local api requests by the
            viewers, operates the gateways and syncs with remote nodes.
        """
        # internal api processor that handles all the actual work:
        self.internal_api_queue = queue.Queue()
        self.internal_api_thread = threading.Thread(target=\
            self.internal_api_processor)
        self.internal_api_thread.start()

        # unix file socket api request reader:
        self.api_socket = api_socket
        self.api_thread = threading.Thread(target=\
            self.api_socket_processor)
        self.api_thread.start()

        # process continuous timed actions:
        while not self.terminate and not self.api_processor_terminated:
            time.sleep(1)
        sys.exit(0)
