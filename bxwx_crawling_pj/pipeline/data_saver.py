from bxwx_crawling_pj.models.save_task import SaveTask
from bxwx_crawling_pj.pipeline.task_worker import TaskWorker
from bxwx_crawling_pj.utils.task_tracer import TaskTracer


class DataSaver(TaskWorker):

    def __init__(self, save_path: str, task_tracer: TaskTracer = None):
        self.save_path = save_path
        self.task_tracer = task_tracer

    def deal_task(self, save_task: SaveTask):
        # print('cid:[%d] - chapter [%s] of book [%s] saved in [%s]' %
             # (save_task.chapter_id, save_task.chapter_name, save_task.book_identification, self.save_path))
        #print('content [%s] ...' % save_task.processed_chapter_content[0: 15])

        if save_task.chapter_id % 100 == 0:
            print('cid:[%d] - chapter [%s] of book [%s] saved in [%s]' %
                    (save_task.chapter_id, save_task.chapter_name, save_task.book_identification, self.save_path))

        if self.task_tracer is not None:
            self.task_tracer.dealt(1)
