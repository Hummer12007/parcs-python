from node_info import create_node_info
import json


class NodeLink:
    id = 0

    def __init__(self, ip, port,  info=None):
        self.id = NodeLink.id
        self.ip = ip
        self.port = port
        self.info = info
        self.enabled = True
        NodeLink.id += 1

    def serialize(self):
        return {
            'id': self.id, 'ip': self.ip, 'port': self.port, 'info': self.info.serialize(),
            'enabled':self.enabled
        }

    def __str__(self):
        return "%s:%d)" % (self.ip, self.port)


def create_node_link(json):
    return NodeLink(json['ip'], json['port'],  create_node_info(json['info']))

# def add_node(self, node_map):
#     ip = node_map['ip']
#     if ip == self.conf.ip:
#         ip = 'localhost'
#     port = node_map['port']
#     if len(filter(lambda l: l.ip == ip and l.port == port, self.nodes)) == 0:
#         info_map = node_map['info']
#         self.nodes.append(
#             NodeLink(ip,
#                      port, node_map['rpc_port'],
#                      NodeInfo(info_map['cpu'], info_map['ram'])))
#     else:
#         print('[Master Node] Node with ip {} and port {} already registered.'.format(ip, port))
