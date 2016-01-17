import logging
from threading import Thread
import imp
from parcs_py.file_utils import get_solution_path, get_output_path, get_input_path
import requests
import zerorpc


class ASYNCSolver:
    def __init__(self, solver):
        self.solver = solver

    def __call__(self, *args, **kargs):
        return self.solver.__call__(*args, async=True)

    def __getattr__(self, method):
        return lambda *args, **kargs: self(method, *args, **kargs)


class NoWorkersException(Exception):
    def __init__(self):
        super(NoWorkersException, self).__init__()
        self.message = 'Unable to find workers.'


class Scheduler(Thread):
    def __init__(self, master, scheduled_jobs):
        super(Scheduler, self).__init__()
        self.setDaemon(True)
        self.job_home = master.conf.job_home
        self.workers = master.workers
        self.scheduled_jobs = scheduled_jobs

    def run(self):
        while True:
            job = self.scheduled_jobs.get()
            job_id = job.id
            log.info('Job %d enqueued.' % job_id)
            selected_workers = []
            try:
                job.start_job()
                rpc_workers, selected_workers = self.init_workers(job_id)

                if len(rpc_workers) == 0:
                    raise NoWorkersException()

                solution_module_path = get_solution_path(self.job_home, job_id)
                solution_module = imp.load_source('solver_module_%d' % job_id, solution_module_path)
                log.info('Loaded solution from %s.' % solution_module_path)

                solver = solution_module.Solver(rpc_workers, get_input_path(self.job_home, job_id),
                                                get_output_path(self.job_home, job_id))
                solver.solve()
                job.end_job()
            except Exception as e:
                job.end_job(True, e.message)
            finally:
                self.destroy_workers(selected_workers, job_id)

    def init_workers(self, job_id):
        try:
            log.info('Starting workers...')
            active_workers = []
            workers_rpc_urls = []
            for worker in filter(lambda w: w.enabled, self.workers):
                response = requests.post(
                    'http://localhost:{}/api/internal/job'.format(worker.port),
                    files={'solution': open(get_solution_path(self.job_home, job_id), 'rb')},
                    data={'job_id': job_id}
                )
                if response.status_code == 200:
                    rpc_port = response.json()['port']
                    workers_rpc_urls.append('tcp://{}:{}'.format(worker.ip, rpc_port))
                    active_workers.append(worker)
                else:
                    log.warning('Unable to run RPC on %s.', worker.ip)
            log.debug('Obtained RPC urls: %s', workers_rpc_urls)
            rpc_workers = []
            for url in workers_rpc_urls:
                client = zerorpc.Client(timeout=None, heartbeat=None)
                client.connect(url)
                rpc_workers.append(wrap_solver(client))
            log.info('Started %d workers.', len(rpc_workers))
            return rpc_workers, active_workers
        except Exception as e:
            return [], []

    def destroy_workers(self, selected_workers, job_id):
        if len(selected_workers) == 0:
            return
        log.info('Stopping %d workers.' % len(selected_workers))
        for worker in selected_workers:
            response = requests.delete(
                'http://localhost:%d/api/internal/rpc/%d' % (worker.port, job_id))
            if response.status_code == 200:
                log.debug('RPC server on %s stopped.', worker.ip)
            else:
                log.warning('Unable to stop RPC server on %s.', worker.ip)
        log.info('%d workers where stopped.' % len(selected_workers))


log = logging.getLogger('Job Scheduler')


def wrap_solver(solver):
    return ASYNCSolver(solver)
