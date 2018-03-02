"""TCP server.

Multithreaded TCP server for the clicker.
"""

import threading
import socketserver
import time
import logging


class ClickerConnectionHandler(socketserver.StreamRequestHandler):
    """Handler to the TCP connections.

    Methods setup(), finish() and handle() are callbacks. The callbacks are
    exepcted to be executed by a thread (one thread per connection).
    """

    def setup(self):
        """Call at the time of establishing the connection.

        This is a callback.
        """
        super().setup()

        self.logger = logging.getLogger(
            'Connection {}'.format(self.client_address[0]))
        self.logger.info('Connected')
        self.server.clicker_server.register_connection(self)

    def finish(self):
        """Call when the connection is closing.

        This is a callback.
        """
        self.server.clicker_server.deregister_connection(self)

        self.logger.info('Disconnected')
        super().finish()

    def handle(self):
        """Handle the new connection.

        This is a callback. Waits for the incomming data and passes it to
        the server.
        """
        try:
            while True:
                # Wait for a line of data and strip all white characters
                data = self.rfile.readline().strip()
                if not data:
                    break

                # Decode the incomming data
                data = data.decode('ASCII')

                self.logger.debug('Data received: "%s"', data)

                # Pass it to the server for handling
                self.server.clicker_server.handle_message(
                    self.client_address[0], data)

        except BrokenPipeError:
            self.logger.info('Connection broken')
        except ConnectionResetError:
            self.logger.info('Connection reset error')
        except OSError:
            self.logger.info('OSError')

    def send_message(self, message):
        """Send the message to the client.

        A new-line character will be added to the end of the message.
        """
        self.logger.debug('Sending message: "%s"', message)
        self.wfile.write((message+'\n').encode())


class ClickerServer:
    """TCP server for the Clicker application.

    Uses the threaded TCP server from the standard library to listen for TCP
    connections. Once a TCP connection is made a new thread is created to
    handle the incoming data and the connection is also registered in a list
    withing this object.

    The incoming data is passed to this object method handle_message().
    Outgoing data is passed to the connections that have been registered
    in the connections list.

    The TCP server runs in a thread and also creates a separate thread for each
    connection.
    """

    def __init__(self, host, port, server_messaging):
        """Initialize the server.

        The server will be started on (host, port) as a background thread.
        """
        self.logger = logging.getLogger('Clicker server')

        self.host = host
        self.port = port

        self.connections = []
        self.connections_lock = threading.Lock()

        self.should_stop = False

        self.server_messaging = server_messaging
        self.server_messaging.server_register_callback('send_message', self.send_message)
        self.server_checking_thread = threading.Thread(target=self.message_reader)
        self.server_checking_thread.start()

        self._setup_server()

    def _setup_server(self):
        """Private method to start the TCP server."""
        socketserver.ThreadingTCPServer.allow_reuse_address = True
        self.server = socketserver.ThreadingTCPServer(
            (self.host, self.port), ClickerConnectionHandler)

        # Register itself with the TCP server. The TCP handlers have access to
        # this reference and therefore can communicate with the ClickerServer
        # object
        self.server.clicker_server = self

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        self.logger.info('Server thread running in the background.')
        self.logger.info('TCP/IP: %s', self.server.server_address)

    def message_reader(self):

        logging.getLogger('Server Messages Checker').info('Thread starting')
        while not self.should_stop:
            self.server_messaging.server_wait(timeout=0.1)

    def send_message(self, message_from_gui):
        ip, message = message_from_gui
        self.logger.debug('Sending a message "%s" to %s', message, ip)

        with self.connections_lock:

            # Iterate reversed because there might be old connections at the front
            for connection in reversed(self.connections):
                if ip == connection.client_address[0]:
                    connection.send_message(message)
                    break

    def register_connection(self, connection):
        """Register a connection with the ClickerServer.

        The TCP handlers use this method to register themselves so that the
        application logic can send messages to the clients.
        """
        with self.connections_lock:
            self.connections.append(connection)
            self.server_messaging.server_post(
                'connected', connection.client_address[0])

    def deregister_connection(self, connection):
        """Remove the client registration.

        The clients remove themselves after the connection is closed.
        """
        with self.connections_lock:
            self.connections.remove(connection)
            self.server_messaging.server_post(
                'disconnected', connection.client_address[0])

    def stop(self):
        """Finalize the server."""
        # TODO: Kill all open connections

        self.should_stop = True
        self.server.shutdown()
        self.server.server_close()

    def broadcast(self, message):
        """Send a message to all connected clients."""
        self.logger.debug('Broadcasting: "%s"', message)

        with self.connections_lock:
            if not self.connections:
                self.logger.debug('Broadcasting a message but there are no '
                                  'active connections')

            for connection in self.connections:
                try:
                    connection.send_message(message)
                except ConnectionError:
                    pass

    def handle_message(self, ip, message):
        """Handle the message sent by a client.

        This is a callback that is called by the TCP client after a message is
        received.
        """
        self.logger.info('Handling message from %s: "%s"', ip, message)
        self.server_messaging.server_post('received', (ip, message))

    def connected_clients_count(self):
        """Return the number of connected clients."""
        return len(self.connections)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    HOST, PORT = "localhost", 10000

    server = ClickerServer(HOST, PORT)

    for _ in range(10):
        time.sleep(1)
        server.broadcast('Hello')

    server.stop()
