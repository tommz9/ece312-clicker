"""TCP server.

Multithreaded TCP echo server.
"""

import socketserver
import logging
import click
import signal
from functools import partial
import threading


class EchoConnectionHandler(socketserver.StreamRequestHandler):
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

        self.server.list_of_connections.append(self)

    def finish(self):
        """Call when the connection is closing.

        This is a callback.
        """

        self.logger.info('Disconnected')
        self.server.list_of_connections.remove(self)

        super().finish()

    def handle(self):
        """Handle the new connection.

        This is a callback. Waits for the incomming data and passes it to
        the server.
        """


        try:
            while True:
                # Wait for a line of data and strip all white characters
                data = self.rfile.readline()

                if not data:
                    break

                self.logger.info('Data received: "%s"', data.decode('ASCII').strip())

                # Send it back to the client it to the server for handling
                self.wfile.write(data)

        except BrokenPipeError:
            self.logger.info('Connection broken')
        except ConnectionResetError:
            self.logger.info('Connection reset error')
        except OSError:
             self.logger.info('OSError')


def interrupt_handler(signal, frame, server):
    logging.getLogger('EchoServer').info("SIGINT received")
    server.shutdown()

    for connection in server.list_of_connections:
        try:
            connection.connection.shutdown(1)
        except Exception:
            # Ignore errors and try to close all connections
            pass

    logging.getLogger('EchoServer').info("Server shutdown")


@click.command(help='A simple TCP server that accepts connections and echoes all received data.')
@click.option('--host', default='0.0.0.0', help='The address the TCP server listens on.')
@click.option('--port', default=2001, help='The port the TCP server listens on.')
def echo_server(host, port):
    logging.basicConfig(level=logging.INFO)

    # Configure the server
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    server = socketserver.ThreadingTCPServer(
        (host, port), EchoConnectionHandler)

    # Used to close the connections when the server is done
    server.list_of_connections = []

    # Catch SIGINT
    signal.signal(signal.SIGINT, partial(interrupt_handler, server=server))


    logging.getLogger('EchoServer').info("Starting the server at %s:%i", host, port)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    server_thread.join()

    server.server_close()
    logging.getLogger('EchoServer').info("Server closed")


if __name__ == "__main__":
    echo_server()
