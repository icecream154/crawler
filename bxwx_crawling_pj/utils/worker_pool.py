from threading import Thread

from bxwx_crawling_pj.models.task import AbstractTask
from bxwx_crawling_pj.pipeline.task_worker import TaskWorker
from bxwx_crawling_pj.utils.task_pool import TaskPool
from bxwx_crawling_pj.utils.task_pool import register_worker


class WorkerPool:
    """ A worker pool can set up a bunch of threads as workers to deal tasks in a specified task pool
    """

    def __init__(self, max_workers: int, max_task_capacity: int, worker: TaskWorker, is_daemon: bool = False):
        """
        max workers in concurrency, max capacity of task pool and
        specified worker is needed when a worker pool is initialized
        :param max_workers: number of workers(Threads) in pool
        :type max_workers: int
        :param max_task_capacity: maximum number of stored tasks in pool
        :type max_task_capacity: int
        :param worker: an instance of a specified subclass of TaskWorker with certain deal_task method
        :type worker: TaskWorker
        :param is_daemon: the pool will be shut down when the main thread exit
                            regardless of situation of the workers if is_daemon is True
        :type is_daemon: bool
        """
        self.is_daemon = is_daemon
        self.max_workers = max_workers
        self.task_pool = TaskPool(max_task_capacity)
        self.executors = []
        for executor_id in range(self.max_workers):
            """
            One worker refers to one thread in this implementation,
            however this is not true parallelism in CPython.
            If computationally intensive tasks are submitted to the pool,
            workers should in different threads or processes at operating system level.
            """
            self.executors.append(Thread(target=register_worker, args=(self.task_pool, worker), daemon=self.is_daemon))

    def start_working(self):
        """
        start all the workers(threads)
        """
        for executor_id in range(self.max_workers):
            self.executors[executor_id].start()

    def submit(self, task: AbstractTask):
        """
        submit a task to the task pool
        :param task: task to submit
        :type task: AbstractTask
        """
        self.task_pool.submit(task)
