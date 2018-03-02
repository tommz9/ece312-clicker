# ece312_clicker

This is a simple voting server developed for the third laboratory in the course ECE312 at Univerity of Alberta.

Features:
 - listens on a TCP port for multiple connections
 - the user can select a question and open a new poll
 - broadcasts the status to the clients
 - displays the results of voting

This package containts two additional servers besides the voting server:
 - Echo Server: A TCP server that accepts connections and echos every line it receives
 - Toggle Server: A TCP server that periodically sends "active" and "inactive" to connected clients
 
## Usage

All examples assume that the application is installed in a virtual environmet.

To run the server GUI application:

```shell
cd ece312-clicker
source venv/bin/activate
python -m ece312_clicker.gui
```

To run the Echo Server:

```shell
cd ece312-clicker
source venv/bin/activate
python -m ece312_clicker.echo_server
```

To run the Toggle Server:

```shell
cd ece312-clicker
source venv/bin/activate
python -m ece312_clicker.toggle_server
```
### TCP ports

The default TCP ports are as follows:

| Server | Port |
| ------ | ---- |
| Clicker server with GUI | 2000 |
| Echo server | 2001 |
| Toggle server | 2002 |

## Installation

Example of installation in a separate virtual environment:

```shell
git clone https://github.com/tommz9/ece312-clicker.git
cd ece312-clicker
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Requirements

Requirements are handelend by setup.py.

 - click: for the command line parameters

# Licence

MIT

# Authors

`ece312_clicker` was written by `Tomas Barton <tommz9@gmail.com>`_.
