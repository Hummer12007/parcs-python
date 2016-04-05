import socket


def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    address, port = s.getsockname()
    s.close()
    return port
