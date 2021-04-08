from bxwx_crawling_pj.models.save_task import SaveTask
from bxwx_crawling_pj.pipeline.task_worker import TaskWorker
from bxwx_crawling_pj.utils.task_tracer import TaskTracer


class DataSaver(TaskWorker):

    def __init__(self, task_tracer: TaskTracer = None):
        self.task_tracer = task_tracer

    def deal_task(self, save_task: SaveTask):
        print('cid:[%d] - chapter [%s] of book [%s] saved' %
                (save_task.chapter_id, save_task.chapter_name, save_task.book_identification))

        if self.task_tracer is not None:
            self.task_tracer.dealt(done_num=1)

    def done_task(self):
        pass
