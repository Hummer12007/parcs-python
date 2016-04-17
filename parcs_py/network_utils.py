import socket
from netifaces import interfaces, ifaddresses, AF_INET


def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    address, port = s.getsockname()
    s.close()
    return port


def get_ip():
    for interfaceName in interfaces():
        addresses = [i['addr'] for i in ifaddresses(interfaceName).setdefault(AF_INET, [{'addr': 'No IP addr'}])]
        address = str(addresses[0])
        if address.startswith('192.'):
            return address
    return None
