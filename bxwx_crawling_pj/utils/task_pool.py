from threading import Semaphore

from bxwx_crawling_pj.pipeline.task_worker import TaskWorker


class TaskPool:
    """ A pool to store tasks to be done by a certain worker

    Attributes:
        max_capacity: maximum number of stored tasks in pool
        task_list: list to store the tasks
        task_count_sema: semaphore to indicates how many tasks are left in pool
        task_limit_sema: semaphore to indicates how many tasks can be added to pool
    """

    def __init__(self, max_capacity: int):
        """
        only max capacity is needed when initialized
        :param max_capacity: maximum number of stored tasks in pool
        :type max_capacity: int
        """
        self.max_capacity = max_capacity
        self.task_list = []
        self.task_count_sema = Semaphore(0)
        self.task_limit_sema = Semaphore(max_capacity)

    def fetch(self):
        """
        fetch a task from the pool to deal, block if there is no task in the pool
        :return: a task fetched from the pool
        :rtype: AbstractTask
        """
        self.task_count_sema.acquire()
        re_task = self.task_list.pop()
        self.task_limit_sema.release()
        return re_task

    def submit(self, task):
        """
        submit a task to the pool, block if number of tasks in the pool reaches max capacity
        :param task: a task to be stored in the pool
        :type task: AbstractTask
        """
        self.task_limit_sema.acquire()
        self.task_list.append(task)
        self.task_count_sema.release()


def register_worker(task_pool: TaskPool, worker: TaskWorker):
    """
    register a worker to a task pool and deal the task continuously
    :param task_pool: the pool that stores tasks
    :type task_pool: TaskPool
    :param worker: worker to deal the task in pool with deal_task method
    :type worker: TaskWorker
    """

    while True:
        task = task_pool.fetch()
        worker.deal_task(task)
