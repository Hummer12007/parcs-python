from cpuinfo import cpuinfo


class NodeInfo:
    def __init__(self, cpu, ram):
        self.cpu = cpu
        self.ram = ram

    def serialize(self):
        return {'cpu': self.cpu, 'ram': self.ram}


def get_node_info_for_current_machine():
    # TODO
    return NodeInfo(cpuinfo.get_cpu_info()['brand'], '4 GB')


def create_node_info(json):
    return NodeInfo(json['cpu'], json['ram'])
