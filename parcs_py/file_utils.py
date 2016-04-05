import shutil
import tempfile

import os
import logging

SOLUTION_FILE_NAME = 'solution.py'
INPUT_FILE_NAME = 'input.txt'
OUTPUT_FILE_NAME = 'output.txt'


def store_file(afile, file_path):
    try:
        afile.save(file_path)
        log.info('File was stored to %s.', file_path)
        return True
    except Exception as e:
        log.info('Error while file storing to %s.', file_path)
        return False


def store_job_file(job_home, afile, job_id, file_name):
    dir_path = os.path.join(job_home, str(job_id))
    file_path = os.path.join(dir_path, file_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    store_file(afile, file_path)
    log.debug('File %s was saved.', str(file_path))


def store_solution(job_home, afile, job_id):
    store_job_file(job_home, afile, str(job_id), SOLUTION_FILE_NAME)


def store_input(job_home, afile, job_id):
    store_job_file(job_home, afile, str(job_id), INPUT_FILE_NAME)


def store_output(job_home, afile, job_id):
    store_job_file(job_home, afile, str(job_id), OUTPUT_FILE_NAME)


def get_solution_path(job_home, job_id):
    return os.path.join(job_home, str(job_id), SOLUTION_FILE_NAME)


def get_input_path(job_home, job_id):
    return os.path.join(job_home, str(job_id), INPUT_FILE_NAME)


def get_output_path(job_home, job_id):
    return os.path.join(job_home, str(job_id), OUTPUT_FILE_NAME)


def get_job_directory(job_home, job_id):
    return os.path.join(job_home, str(job_id))


def clear_directory(directory):
    try:
        shutil.rmtree(directory)
        # print '>> Remove dir stub'
        log.info('Directory %s was cleared.', directory)
    except Exception as e:
        log.warn('Error while clearing %s directory.', directory)


def setup_working_directory():
    try:
        directory = tempfile.mkdtemp()
        log.info('Temporary directory %s was created.', directory)
        clear_directory(directory)
        return directory
    except Exception as e:
        log.fatal('Error while working directory setup.')
        raise e


log = logging.getLogger('File Utils')
