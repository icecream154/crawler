from threading import Semaphore

from bxwx_crawling_pj.pipeline.task_worker import TaskWorker


class TaskPool:
    def __init__(self, max_capacity: int):
        self.max_capacity = max_capacity
        self.task_list = []
        self.task_count_sema = Semaphore(0)
        self.task_limit_sema = Semaphore(max_capacity)

    def fetch(self):
        self.task_count_sema.acquire()
        re_task = self.task_list.pop()
        self.task_limit_sema.release()
        return re_task

    def submit(self, task):
        self.task_limit_sema.acquire()
        self.task_list.append(task)
        self.task_count_sema.release()


def register_worker(task_pool: TaskPool, worker: TaskWorker):
    while True:
        task = task_pool.fetch()
        worker.deal_task(task)
