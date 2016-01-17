import imp
from multiprocessing import Process
from parcs_py.network_utils import find_free_port
import zerorpc
import json
from abc import abstractmethod
from node_info import get_node_info_for_current_machine
from node_link import NodeLink
from file_utils import get_solution_path, get_input_path, get_output_path, clear_directory
import requests
import logging

log = None


class Node:
    def __init__(self, conf):
        self.conf = conf
        self.info = get_node_info_for_current_machine()
        clear_directory(self.conf.job_home)

    @abstractmethod
    def is_master_node(self):
        pass

    @staticmethod
    def create_node(conf):
        if conf.master:
            return MasterNode(conf)
        else:
            node = WorkerNode(conf)
            node.register_on_master()
            return node


class WorkerNode(Node):
    def __init__(self, conf):
        Node.__init__(self, conf)
        global log
        log = logging.getLogger('Worker Node')
        self.rpc_thread = None
        self.master = NodeLink(conf.master_ip, conf.master_port)
        log.info('Started on %s:%d; Job directory - %s.', conf.ip, conf.port, conf.job_home)

    def is_master_node(self):
        return False

    def register_on_master(self):
        data = {'ip': self.conf.ip, 'port': self.conf.port,
                'info': {'cpu': self.info.cpu, 'ram': self.info.ram}}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post('http://%s:%s/api/internal/worker' % (self.master.ip, self.master.port),
                          data=json.dumps(data), headers=headers)
        if r.status_code == 200:
            log.info('Registered to master on %s:%d.',
                     self.conf.master_ip, self.conf.master_port)
        else:
            log.warning('Unable to register to master on %s:%d.', self.conf.master_ip, self.conf.master_port)

    def start_rpc(self, job_id):
        self.rpc_thread = RPCThread(self.conf, job_id)
        self.rpc_thread.start()
        return self.rpc_thread.rpc_port

    def stop_rpc(self):
        self.rpc_thread.stop()
        self.rpc_thread = None


class MasterNode(Node):
    def __init__(self, conf):
        Node.__init__(self, conf)
        global log
        log = logging.getLogger('Master Node')
        self.jobs = []
        self.workers = []
        log.info('Started on %s:%d; Job directory - %s.', conf.ip, conf.port,
                 conf.job_home)

    def is_master_node(self):
        return True

    def register_worker(self, node_link):
        if len(filter(lambda l: l.ip == node_link.ip and l.port == node_link.port, self.workers)) == 0:
            self.workers.append(node_link)
            return True
        else:
            log.warning('Unable to register node %s:%d because it is already registered.', node_link.ip, node_link.port)
            return False

    def find_worker(self, worker_id):
        workers_list = filter(lambda w: w.id == worker_id, self.workers)
        return None if len(workers_list) == 0 else workers_list[0]

    def delete_worker(self, worker_id):
        prev_len = len(self.workers)
        self.workers = filter(lambda w: w.id != worker_id, self.workers)
        return prev_len != len(self.workers)

    def add_job(self, job):
        self.jobs.append(job)

    def find_job(self, job_id):
        filtered = filter(lambda j: j.id == job_id, self.jobs)
        return None if len(filtered) == 0 else filtered[0]


class RPCThread(Process):
    log = logging.getLogger('RPC Thread')

    def __init__(self, conf, job_id):
        super(RPCThread, self).__init__()
        self.job_id = job_id
        self.conf = conf
        self.rpc_port = find_free_port()

    def run(self):
        solution_module = imp.load_source('solver_module_%d' % self.job_id,
                                          get_solution_path(self.conf.job_home, self.job_id))
        solver = solution_module.Solver()
        rpc_server = zerorpc.Server(solver, heartbeat=None)
        try:
            rpc_server.bind('tcp://0.0.0.0:%d' % self.rpc_port)
            log.info('Worker on localhost:%d for %d job started.', self.rpc_port, self.job_id)
            rpc_server.run()
        except Exception as e:
            log.warning('23 181 75 18er on localhost for %d job because of %s', self.job_id, e.message)

    def stop(self):
        pass
