import imp
from threading import Thread

import time

from parcs_py.network_utils import find_free_port
import Pyro4
import json
from abc import abstractmethod
from node_info import get_node_info_for_current_machine
from node_link import NodeLink
from file_utils import get_solution_path, setup_working_directory
import requests
import logging

log = None


class Node:
    def __init__(self, conf):
        self.conf = conf
        self.info = get_node_info_for_current_machine()

    @abstractmethod
    def is_master_node(self):
        pass

    @staticmethod
    def create_node(conf):
        if conf.master:
            return MasterNode(conf)
        else:
            node = WorkerNode(conf)
            return node


class WorkerNode(Node):
    def __init__(self, conf):
        Node.__init__(self, conf)
        global log
        log = logging.getLogger('Worker Node')
        self.rpc_thread = None
        self.master = NodeLink(conf.master_ip, conf.master_port)
        self.connected = False
        log.info('Started on %s:%d; Job directory: %s.', conf.ip, conf.port, conf.job_home)
        self.reconnector = MasterReconnector(self)
        self.reconnector.start()

    def is_master_node(self):
        return False

    def register_on_master(self):
        data = {'ip': self.conf.ip, 'port': self.conf.port,
                'info': {'cpu': self.info.cpu, 'ram': self.info.ram}}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        try:
            r = requests.post('http://%s:%s/api/internal/worker' % (self.master.ip, self.master.port),
                              data=json.dumps(data), headers=headers)
            if r.status_code == 200:
                self.connected = True
                log.info('Registered to master on %s:%d.',
                         self.conf.master_ip, self.conf.master_port)
            else:
                self.connected = False
                log.warning('Unable to register to master on %s:%d.', self.conf.master_ip, self.conf.master_port)
        except Exception as e:
            self.connected = False
            log.warning('Unable to register to master on %s:%d because of %s.', self.conf.master_ip,
                        self.conf.master_port, str(e))

    def connection_with_master_lost(self):
        self.connected = False
        log.warning('Connection with master %s:%d lost.', self.master.ip, self.master.port)

    def start_rpc(self, job_id):
        self.rpc_thread = RPCThread(self.conf.ip, job_id, self.conf.job_home)
        uri = self.rpc_thread.register_algorithm_module()
        self.rpc_thread.start()
        log.info("Started RPC for %d job on %s.", job_id, uri)
        return uri

    def stop_rpc(self):
        self.rpc_thread.stop()
        log.info("Stopped RPC for %d job.", self.rpc_thread.job_id)
        self.rpc_thread = None


class MasterReconnector(Thread):
    def __init__(self, worker_node):
        super(MasterReconnector, self).__init__()
        self.setDaemon(True)
        self.worker_node = worker_node

    def run(self):
        while True:
            try:
                time.sleep(1)
                log.info('Trying to connect')
                response = requests.get('http://%s:%s/api/internal/heartbeat' % (
                    self.worker_node.conf.ip, self.worker_node.conf.port))
                if response.status_code == 200:
                    break
            except Exception as e:
                print(e)
                pass
        while True:
            if self.worker_node.connected:
                try:
                    response = requests.get('http://%s:%s/api/internal/heartbeat' % (
                        self.worker_node.master.ip, self.worker_node.master.port))
                    if response.status_code != 200:
                        self.worker_node.connection_with_master_lost()
                except Exception as e:
                    self.worker_node.connection_with_master_lost()
            else:
                self.worker_node.register_on_master()
            time.sleep(5)


class MasterNode(Node):
    def __init__(self, conf):
        Node.__init__(self, conf)
        global log
        log = logging.getLogger('Master Node')
        self.jobs = []
        self.workers = []
        log.info('Started on %s:%d; Job directory: %s.', conf.ip, conf.port,
                 conf.job_home)
        self.heartbeat = Heartbeat(self)
        self.heartbeat.start()

    def is_master_node(self):
        return True

    def register_worker(self, node_link):
        if len(filter(lambda l: l.ip == node_link.ip and l.port == node_link.port, self.workers)) == 0:
            self.workers.append(node_link)
            ret = True
        else:
            log.warning('Unable to register node %s:%d because it is already registered.', node_link.ip, node_link.port)
            ret = False
        print(node_link)
        print(self.workers)
        return ret

    def find_worker(self, worker_id):
        workers_list = filter(lambda w: w.id == worker_id, self.workers)
        return None if len(workers_list) == 0 else workers_list[0]

    def delete_worker(self, worker_id):
        prev_len = len(self.workers)
        self.workers = filter(lambda w: w.id != worker_id, self.workers)
        return prev_len != len(self.workers)

    def abort_job(self, job_id):
        result = False
        for j in self.jobs:
            if j.id == job_id:
                j.abort_job()
                result = True
        return result

    def add_job(self, job):
        self.jobs.append(job)
        log.info("Job was added.")

    def find_job(self, job_id):
        filtered = filter(lambda j: j.id == job_id, self.jobs)
        return None if len(filtered) == 0 else filtered[0]


class Heartbeat(Thread):
    def __init__(self, master_node):
        super(Heartbeat, self).__init__()
        self.setDaemon(True)
        self.master_node = master_node
        self.log = logging.getLogger('Heartbeat')

    def run(self):
        while True:
            time.sleep(5)
            self.log.debug('%d workers is about to check.', len(self.master_node.workers))
            dead_workers = []
            for worker in self.master_node.workers:
                try:
                    response = requests.get('http://%s:%s/api/internal/heartbeat' % (worker.ip, worker.port))
                    if response.status_code != 200:
                        dead_workers.append(worker.id)
                except Exception as e:
                    dead_workers.append(worker.id)
            if len(dead_workers) == 0:
                self.log.debug('All workers alive.')
            else:
                self.log.warn('%d workers are dead.', len(dead_workers))
            for dead_worker in dead_workers:
                self.master_node.delete_worker(dead_worker)


class RPCThread(Thread):
    log = logging.getLogger('RPC Thread')

    def __init__(self, ip, job_id, job_home):
        super(RPCThread, self).__init__()
        self.setDaemon(True)
        self.job_id = job_id
        self.job_home = job_home
        try:
            self.daemon = Pyro4.Daemon(host=ip)
            RPCThread.log.info('Pyro4 daemon created successfully.')
        except Exception as e:
            RPCThread.log.error('Unable to create pyro4 daemon.')

    def register_algorithm_module(self):
        if not self.daemon:
            return None
        try:
            algorithm_module = imp.load_source('solver_module_%d' % self.job_id,
                                               get_solution_path(self.job_home, self.job_id))
            solver = algorithm_module.Solver()
            uri = self.daemon.register(solver)
            RPCThread.log.info("Algorithm module registered on %s.", uri)
            return uri
        except Exception as e:
            RPCThread.log.error("Unable to create algorithm module or register it: %s.", str(e))
            return None

    def run(self):
        try:
            self.daemon.requestLoop()
        except Exception as e:
            log.warning('Error of %s.', str(e))

    def stop(self):
        self.daemon.shutdown()
