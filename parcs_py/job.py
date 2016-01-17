import datetime
import logging


class Job:
    id = 0

    def __init__(self, name):
        self.name = name.upper()
        self.failed = None
        self.id = Job.id
        self.start_time = None
        self.duration = None
        self.duration_str = None
        self.status = None
        Job.id += 1
        log.info('Job %d created.', self.id)

    def start_job(self):
        self.start_time = datetime.datetime.now()
        log.info('Job %d started.', self.id)

    def end_job(self, failed=False, status=None):
        self.status = status
        self.failed = failed
        self.duration = (datetime.datetime.now() - self.start_time).seconds
        hours, remainder = divmod(self.duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.duration_str = '%s:%s:%s' % (hours, minutes, seconds)
        log.info('Job %d %s. Duration %s.', self.id, 'ended' if not failed else 'failed', self.duration_str)

    def is_ended(self):
        return False if self.duration is None else True

    def title(self):
        return '%s [error: %s]' % (self.name, self.status) if self.failed else self.name


log = logging.getLogger('Job')
