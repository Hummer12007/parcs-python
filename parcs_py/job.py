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
        self.aborted = False
        Job.id += 1
        log.info('Job %d created.', self.id)

    def start_job(self):
        self.start_time = datetime.datetime.now()
        log.info('Job %d started.', self.id)

    def abort_job(self):
        self.aborted = True
        self.status = "Aborted"
        self.failed = True
        if self.start_time:
            self.duration = (datetime.datetime.now() - self.start_time).seconds
            self.duration_str = Job.get_duration_str(self.duration)
            self.duration_str = "ABORTED [%s]" % self.duration_str
        else:
            self.duration = -1
            self.duration_str = "ABORTED"
        log.info("Job %d was aborted.", self.id)

    def end_job(self, failed=False, status=None):
        self.status = status
        self.failed = failed
        self.duration = (datetime.datetime.now() - self.start_time).seconds
        self.duration_str = Job.get_duration_str(self.duration)
        log.info('Job %d %s. Duration %s.', self.id, 'ended' if not failed else 'failed', self.duration_str)

    @staticmethod
    def get_duration_str(duration):
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '%s:%s:%s' % (hours, minutes, seconds)

    def is_ended(self):
        return False if self.duration is None else True

    def title(self):
        return '%s [reason: %s]' % (self.name, self.status) if self.failed else self.name


log = logging.getLogger('Job')
