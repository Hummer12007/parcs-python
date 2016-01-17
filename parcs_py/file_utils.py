import shutil
import os
import logging

SOLUTION_FILE_NAME = 'solution.py'
INPUT_FILE_NAME = 'input.txt'
OUTPUT_FILE_NAME = 'output.txt'


def store_file(afile, file_path):
    afile.save(file_path)
    log.info('File was stored to %s.' , file_path)


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

def get_job_directory(job_home,job_id):
    return os.path.join(job_home,str(job_id))

def clear_directory(adir):
    try:
        shutil.rmtree(adir)
        # print '>> Remove dir stub'
    except Exception as e:
        pass
    log.info('Directory %s was removed.' , adir)
log = logging.getLogger('File Utils')