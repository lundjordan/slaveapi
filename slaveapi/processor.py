import logging
import time

from gevent import queue, spawn

from .actions.results import ActionResult, RUNNING, FAILURE
from .global_state import messages, log_data
from .util import logException

log = logging.getLogger(__name__)


class Processor(object):
    max_jobs = 20

    def __init__(self):
        self._message_loop = None
        self.stopped = False
        self.workers = []
        self.work_queue = queue.Queue()

    def configure(self, concurrency):
        self.concurrency = concurrency

    def add_work(self, slave, action, *args, **kwargs):
        res = ActionResult(slave, action.__name__)
        item = (slave, action, args, kwargs, res)
        log.debug("Adding work to queue: %s", item)
        self.work_queue.put(item)
        self._start_worker()
        return res

    def _start_worker(self):
        if len(self.workers) < self.concurrency:
            log.debug("Spawning new worker")
            t = spawn(self._worker)
            t.link(self._worker_done)
            self.workers.append(t)

    def _worker_done(self, t):
        self.workers.remove(t)
        if self.work_queue.qsize() and not self.stopped:
            self._start_worker()

    def _worker(self):
        jobs = 0
        while True:
            try:
                # Reset slave to empty
                log_data.slave = "-.-"
                jobs += 1
                try:
                    item = self.work_queue.get(block=False)
                    if not item:
                        break
                except queue.Empty:
                    break

                log.info("Processing item: %s", item)
                slave, action, args, kwargs, res = item
                log_data.slave = slave
                start_ts = time.time()
                messages.put((RUNNING, item, "In Progress", start_ts))
                res, msg = action(slave, *args, **kwargs)
                log.info("Finished Processing item: %s", item)
                finish_ts = time.time()

                messages.put((res, item, msg, start_ts, finish_ts))

                # todo, bail after max jobs
                if jobs >= self.max_jobs:
                    break
            except Exception, e:
                finish_ts = time.time()
                logException(log.error, "Something went wrong while processing!")
                if item:
                    log.debug("Item was: %s", item)
                messages.put((FAILURE, item, str(e), start_ts, finish_ts))
