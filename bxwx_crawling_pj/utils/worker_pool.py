from threading import Thread

from bxwx_crawling_pj.pipeline.task_worker import TaskWorker
from bxwx_crawling_pj.utils.task_pool import TaskPool
from bxwx_crawling_pj.utils.task_pool import register_worker


class WorkerPool:
    """ A worker pool can set up a bunch of threads as workers to deal tasks in a specified task pool

    """
    def __init__(self, max_workers: int, max_task_capacity: int, worker: TaskWorker, is_daemon: bool = False):
        self.is_daemon = is_daemon
        self.max_workers = max_workers
        self.task_pool = TaskPool(max_task_capacity)
        self.executors = []
        for executor_id in range(self.max_workers):
            self.executors.append(Thread(target=register_worker, args=(self.task_pool, worker), daemon=self.is_daemon))

    def start_working(self):
        for executor_id in range(self.max_workers):
            self.executors[executor_id].start()

    def submit(self, task):
        self.task_pool.submit(task)
