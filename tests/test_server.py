# Sample Test passing with nose and pytest

import socket
import time

from ece312_clicker.server import ClickerServer

def simple_client(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', port))
        # sock.sendall(bytes(message, 'ascii'))
        # response = str(sock.recv(1024), 'ascii')
        # print("Received: {}".format(response))

def test_server_starts():

    # Create the server on a random port
    clickerServer = ClickerServer('localhost', 0)
    port = clickerServer.server.server_address[1]

    # Try to connect to it
    simple_client(port)

    clickerServer.stop()
    # Should not throw

def test_server_registers_clients():
    # Create the server on a random port
    clickerServer = ClickerServer('localhost', 0)
    port = clickerServer.server.server_address[1]

    assert clickerServer.connected_clients_count() == 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock1:
        sock1.connect(('localhost', port))
        time.sleep(0.01)

        assert clickerServer.connected_clients_count() == 1

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock2:
            sock2.connect(('localhost', port))
            time.sleep(0.01)

            assert clickerServer.connected_clients_count() == 2
        time.sleep(0.01)

        assert clickerServer.connected_clients_count() == 1
    time.sleep(0.01)
    assert clickerServer.connected_clients_count() == 0
