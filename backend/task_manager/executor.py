"""
Task executor
"""
import time
import logging
import queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import schedule
from config import DAEMON_WORKERS
from .models import TaskSettings

LOGGER = logging.getLogger(__name__)


def config_checker(json_config):
    try:
        pre_check_fail = ('image' not in json_config.keys() or
                          'persistent_volume' not in json_config.keys() or
                          'name' not in json_config['persistent_volume'].keys() or
                          'mount_path' not in json_config['persistent_volume'].keys() or
                          'shell' not in json_config.keys() or
                          'memory_limit' not in json_config.keys() or
                          'commands' not in json_config.keys() or
                          not isinstance(json_config['commands'], list))
        return not pre_check_fail
    except Exception as _:
        return False


class TaskExecutor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=DAEMON_WORKERS, thread_name_prefix='cloud_scheduler_k8s_worker')
        self.scheduler_thread = Thread(target=self.dispatch)
        self.job_queue = queue.Queue()
        self.max_job_id = 0
        LOGGER.info("Task executor initialized.")

    def start(self):
        if not self.scheduler_thread.isAlive():
            self.scheduler_thread.start()
            LOGGER.info("Task executor started.")
        else:
            LOGGER.info("Task executor already started")

    def _run_job(self, fn, *args, **kwargs):
        self.executor.submit(fn, *args, **kwargs)

    def _ttl_check(self, uuid):
        try:
            TaskSettings.objects.get(uuid=uuid)
        except TaskSettings.DoesNotExist:
            schedule.clear(uuid)
        LOGGER.info(uuid)

    def dispatch(self):
        while True:
            schedule.run_pending()
            for item in TaskSettings.objects.filter(id__gt=self.max_job_id):
                if config_checker(item.container_config):
                    schedule.every(item.ttl_interval).seconds.do(self.job_queue.put,
                                                                 self._ttl_check, uuid=item.uuid).tag(item.uuid)
                else:
                    LOGGER.warning("Task %s has invalid settings", item.uuid)
                if item.id > self.max_job_id:
                    self.max_job_id = item.id
            time.sleep(0.01)
