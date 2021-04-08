from abc import ABC, abstractmethod

from bxwx_crawling_pj.utils.task_tracer import TaskTracer


class TaskWorker(ABC):
    """ Abstract super class of task workers
    """

    @abstractmethod
    def deal_task(self, task):
        pass

    def register_tracer(self, task_tracer: TaskTracer):
        if self.task_tracer is not None:
            self.task_tracer = task_tracer
