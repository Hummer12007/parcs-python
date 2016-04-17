import Pyro4
from flask import Flask, render_template, request, send_from_directory, jsonify, Response
import socket
import ConfigParser
from node import Node
from node_link import create_node_link
from file_utils import get_job_directory, OUTPUT_FILE_NAME, SOLUTION_FILE_NAME, INPUT_FILE_NAME, store_input, \
    store_solution, setup_working_directory
from job import Job
import logging
from Queue import Queue
from network_utils import find_free_port, get_ip
from parcs_py.scheduler import Scheduler


class Config:
    NODE_SECTION = 'Node'
    MASTER_NODE_SECTION = 'Master Node'

    def __init__(self, ip, port, master_ip=None, master_port=None):
        self.master = master_ip is None
        self.ip = ip if ip else get_ip()
        self.port = port if port else find_free_port()
        self.job_home = setup_working_directory()
        self.master_ip = master_ip
        self.master_port = master_port

    @staticmethod
    def load_from_file(config_path):
        configuration = ConfigParser.ConfigParser()
        configuration.read(config_path)

        master = configuration.getboolean(Config.NODE_SECTION, 'master')
        ip = configuration.get(Config.NODE_SECTION, 'ip') if configuration.has_option(Config.NODE_SECTION,
                                                                                             'ip') else None
        port = configuration.getint(Config.NODE_SECTION, 'port') if configuration.has_option(Config.NODE_SECTION,
                                                                                             'port') else None

        if not master:
            master_ip = configuration.get(Config.MASTER_NODE_SECTION, 'ip')
            master_port = configuration.getint(Config.MASTER_NODE_SECTION, 'port')
            return Config(ip, port, master_ip, master_port)
        return Config(ip, port)


def start(conf):
    log.info("Starting...")
    log.info("Configuring Pyro4...")
    log.info("Pyro4 configured.")
    app.node = Node.create_node(conf)
    if app.node.is_master_node():
        app.scheduler = Scheduler(app.node, app.scheduled_jobs)
        app.scheduler.start()
    log.info("Started.")
    app.run(host='0.0.0.0', port=conf.port)


logging.basicConfig(level=logging.INFO)

log = logging.getLogger('PARCS')

app = Flask(__name__)
app.debug = False
app.node = None
app.scheduler = None
app.scheduled_jobs = Queue()


def bad_request():
    return Response(status=400)


def not_found():
    return Response(status=404)


def ok():
    return Response(status=200)


# WEB
@app.route('/')
@app.route('/index')
def index_page():
    return render_template('index.html')


@app.route('/workers', methods=['GET'])
def workers_page():
    if not app.node.is_master_node():
        return render_template('error.html', title='This is not master node.'), 400
    return render_template("workers.html", title='Workers', workers=app.node.workers)


@app.route('/jobs', methods=['GET'])
def jobs_page():
    if not app.node.is_master_node():
        return render_template('error.html', title='This is not master node.'), 400
    return render_template("jobs.html", title='Jobs', jobs=app.node.jobs)


@app.route('/add_job', methods=['GET'])
def add_job_page():
    return render_template('add_job.html',
                           title='Add Job')


@app.route('/about')
def about_page():
    return render_template("about.html")


# Public API
@app.route('/api/worker')
def get_workers():
    if not app.node.is_master_node():
        return bad_request()
    return jsonify(workers=[w.serialize() for w in app.node.workers])


@app.route('/api/worker/<int:worker_id>')
def get_worker(worker_id):
    if not app.node.is_master_node():
        return bad_request()
    worker = app.node.find_worker(worker_id)
    if worker:
        return jsonify(workers=worker.serialize())
    else:
        return not_found()


@app.route('/api/job/<int:job_id>', methods=['DELETE'])
def abort_job(job_id):
    if not app.node.is_master_node():
        return bad_request()
    log.info("Aborting %d job.", job_id)
    result = app.node.abort_job(job_id)
    if result:
        log.info("Job %d aborted.")
    else:
        log.info("Unable to find job %d.", job_id)
    return ok() if result else not_found()


@app.route('/api/worker/<int:worker_id>', methods=['DELETE'])
def delete_worker(worker_id):
    if not app.node.is_master_node():
        return bad_request()
    log.info("Removing %d worker.", worker_id)
    result = app.node.delete_worker(worker_id)
    if result:
        log.info("Worker %d removed.", worker_id)
    else:
        log.warn("Unable to find worker %d.", worker_id)
    return ok() if result else not_found()


@app.route('/api/worker/<int:worker_id>/<state>', methods=['POST'])
def enable_disable_worker(worker_id, state):
    if not app.node.is_master_node():
        return bad_request()
    worker = app.node.find_worker(worker_id)
    if worker is None:
        return bad_request()
    else:
        worker.enabled = True if state == 'enable' else False
        return ok()


@app.route('/api/job/<int:job_id>/<file_name>')
def get_job_file(job_id, file_name):
    if not app.node.is_master_node():
        return bad_request()
    job = app.node.find_job(job_id)
    if not job:
        return not_found()
    if file_name == 'solution':
        return send_from_directory(get_job_directory(app.node.conf.job_home, job.id), SOLUTION_FILE_NAME,
                                   as_attachment=True)
    elif file_name == 'input':
        return send_from_directory(get_job_directory(app.node.conf.job_home, job.id), INPUT_FILE_NAME,
                                   as_attachment=True)
    elif file_name == 'output':
        if job.is_ended():
            return send_from_directory(get_job_directory(app.node.conf.job_home, job.id), OUTPUT_FILE_NAME,
                                       as_attachment=True)
        else:
            return bad_request()
    else:
        return not_found()


@app.route('/api/job', methods=['POST'])
def add_job():
    job_name = request.form.get('job_name')
    solution_file = request.files['solution_file']
    input_file = request.files['input_file']

    job = Job(job_name)

    store_solution(app.node.conf.job_home, solution_file, job.id)
    store_input(app.node.conf.job_home, input_file, job.id)

    app.node.add_job(job)
    log.info('Job %d was scheduled. Scheduled queue size - %d.' % (job.id, app.scheduled_jobs.qsize() + 1))
    app.scheduled_jobs.put(job)

    return render_template('add_job.html', title='Add Job')


# Inernal api
@app.route('/api/internal/heartbeat')
def heartbeat():
    return ok()


@app.route('/api/internal/worker', methods=['POST'])
def register_worker():
    json = request.get_json()
    node_link = create_node_link(json)
    log.info("Worker %s is about to register.", str(node_link))
    result = app.node.register_worker(node_link)
    if result:
        log.info("Worker %s registered.", str(node_link))
        return jsonify(worker=node_link.serialize())
    else:
        return bad_request()


@app.route('/api/internal/job', methods=['POST'])
def add_solution():
    if app.node.is_master_node():
        return bad_request()
    solution_file = request.files['solution']
    job_id = int(request.form.get('job_id'))
    store_solution(app.node.conf.job_home, solution_file, job_id)
    return start_job_rpc_server(job_id)


@app.route('/api/internal/rpc/<int:job_id>', methods=['DELETE'])
def stop_job_rpc_server(job_id):
    if app.node.is_master_node():
        return bad_request()
    app.node.stop_rpc()
    return ok()


@app.route('/api/internal/rpc/<int:job_id>', methods=['POST'])
def start_job_rpc_server(job_id):
    if app.node.is_master_node():
        return bad_request()
    uri = app.node.start_rpc(job_id)
    return jsonify(uri=str(uri))
