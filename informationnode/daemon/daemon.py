
'''
information-node - an advanced tool for data synchronization
Copyright (C) 2015  Information Node Development Team (see AUTHORS.md)

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

import datetime
import json
import logging
import os
import platform
import queue
import signal
import struct
import threading
import time

from informationnode.helper import send_json, recv_json

class FileSocketApiClientHandler(threading.Thread):
    def __init__(self, client):
        super().__init__()
        self.daemon = client.daemon
        self.client = client
        self.socket = client.socket
        self.internal_api_queue = self.daemon.internal_api_queue

    def process_msg(self, msg):
        """ Process an API msg that was received. """
        logging.debug("received msg from: " + str(self.client.address))
        logging.debug("msg contents: " + str(msg))
        if not "action" in msg:
            # whoops this is invalid.
            return False
        if msg["action"] == "ping":
            return self.respond({"action":"pong"})
        elif msg["action"] == "shutdown":
            result = self.respond({"action" : "response",
                "responded_action" : msg["action"],
                "response_type" : "success"})
            self.daemon.terminate()
            return result
        else:
            # unknown action.
            return self.respond({"action" : "response",
                "responded_action" : str(msg["action"]),
                "response_type" : "error",
                "error_info" : "unknown action: \"" +\
                str(msg["action"]) + "\""})

    def respond(self, obj):
        # check the connection still being open:
        if self.client.socket == None:
            # client was already closed.
            return False
        # try to send:
        if not send_json(self.socket, obj):
            # sending failed
            self.socket.close()
            self.client.socket = None
            return False

        return True

    def run(self):
        try:
            recv_buf = b""
            while True:
                # get message from client:
                msg = recv_json(self.socket)
                if msg == None:
                    # nothing received / connection lost.
                    self.socket.close()
                    self.client.socket = None
                    return

                # process received message:
                try:
                    if not self.process_msg(msg):
                        # client was terminated.
                        self.socket.close()
                        self.client.socket = None
                except Exception as e:
                    logging.exception("Error in " +\
                        "FileSocketApiClientHandler.process_msg: " +\
                            str(e))
                    self.socket.close()
                    self.client.socket = None
                    return
        except Exception as e:
            logging.exception("Error in FileSocketApiClientHandler.run: " +\
                str(e))
            self.socket.close()
            self.client.socket = None

class FileSocketApiClient(object):
    def __init__(self, daemon, socket, address):
        self.daemon = daemon
        self.address = address
        self.socket = socket
        self.client_thread = FileSocketApiClientHandler(self)
        self.client_thread.start()

    def force_terminate(self):
        try:
            self.socket.close()
        except (OSError, AttributeError):
            pass
        self.socket = None
 
    def terminated(self):
        if self.socket == None:
            return True
        return False

class Daemon(object):
    def __init__(self, node_path):
        self.node_path = node_path
        self.api_processor_terminated = False
        self.api_socket_processor_terminated = False
        self._terminate = False

        # set up signal handlers:
        if platform.system().lower() != "windows":
            signal.signal(signal.SIGTERM, lambda signal, info: \
                self.sigterm_handler(signal, info))
            signal.signal(signal.SIGHUP, lambda signal, info: \
                self.sighup_handler(signal, info))

        # set up logging to file:
        logging.basicConfig(filename=os.path.join(node_path, "logs",
                "log-" +  datetime.datetime.now().strftime("%Y-%m-%d") +\
                ".txt"),
            filemode='a',
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%H:%M:%S',
            level=logging.DEBUG)
        logging.info("Data server initialized.")

    def terminate(self):
        """ Set the shutdown signal on the daemon and terminate various things
            like the api socket.
        """

        # remove api socket:
        try:
            self.api_socket.close()
        except OSError:
            pass
        if platform.system().lower() != "windows":
            os.remove(os.path.join(self.node_path, "api_access.sock"))

        self._terminate = True
        logging.info("Shutdown initiated...")

    def sigterm_handler(self, signal, unused_info):
        """ SIGTERM handler which will initiate shutdown. """
        logging.debug("sigterm received")
        self.terminate()

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
        try:
            while not self._terminate:
                try:
                    next_msg = self.internal_api_queue.get(timeout=0.5)
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
        except Exception as e:
            logging.exception("unhandled exception in internal_api_processor")
            raise e

    def api_socket_processor(self):
        """ Deals with the outside requests coming into the api socket
            (api_access.sock). Hands off the actual work to the internal api
            processor later by forming the according internal JSON requests.
        """
        logging.debug("[api_socket_processor] starting...")
        try:
            self.api_socket.listen(1)
            logging.debug("[api_socket_processor] now listening")
            clients = {}
            while True:
                # add new client(s):
                c, addr = self.api_socket.accept()
                if self._terminate:
                    logging.debug("[api_socket_processor] shutting down...")
                    for client_k in clients:
                        if not clients[client_k].terminated():
                            clients[client_k].force_terminate()
                    break

                clients[c] = FileSocketApiClient(self, c, addr)
                logging.debug("[api_socket_processor] new client")          

                # throw away clients that have been terminated:
                remove_clients = []
                for client_k in clients:
                    if clients[client_k].terminated():
                        remove_clients.append(client_k)
                for client_k in remove_clients:
                    del(clients[client_k])
            self.api_socket_processor_terminated = True
        except Exception as e:
            logging.exception("unhandled exception in api_socket_processor")

    def run(self, api_socket):
        """ Run the data server which handles local api requests by the
            viewers, operates the gateways and syncs with remote nodes.
        """
        logging.debug("Launching other processing threads...")
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

        logging.debug("Data server main thread starting.")
        
        # process continuous timed actions:
        while not self._terminate or not self.api_processor_terminated:
            time.sleep(1)
        logging.info("Shutting down data server.")
        
        # remove PID file:
        os.remove(os.path.join(self.node_path, "pidfile"))

        os._exit(0)

