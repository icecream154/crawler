from bxwx_crawling_pj.models.process_task import ProcessTask
from bxwx_crawling_pj.models.save_task import SaveTask
from bxwx_crawling_pj.pipeline.task_worker import TaskWorker
from bxwx_crawling_pj.utils.worker_pool import WorkerPool
from bxwx_crawling_pj.utils.task_tracer import TaskTracer


class ContentProcessor(TaskWorker):

    def __init__(self, data_saver_pool: WorkerPool, task_tracer: TaskTracer = None):
        self.data_saver_pool = data_saver_pool
        self.task_tracer = task_tracer

    def deal_task(self, process_task: ProcessTask):
        book_name = process_task.book_identification.split('-')[0]
        self.data_saver_pool.submit(SaveTask(process_task.chapter_id, process_task.book_identification,
                                             process_task.chapter_name,
                                             ContentProcessor._process_content(book_name, process_task.chapter_content))
                                    )

        if self.task_tracer is not None:
            self.task_tracer.dealt(done_num=1, child_task_num=1)

    @staticmethod
    def _process_content(book_name: str, chapter_content: str):
        replace_list = [('    ', '\n    '),
                        ('笔下文学网 www.bixiawenxue.org，最快更新' + book_name + '最新章节！', '\n')]
        filtered_content = ContentProcessor._content_filter(chapter_content, replace_list)
        return filtered_content

    @staticmethod
    def _content_filter(ori_content: str, replace_list: [(str, str)]):
        for rep in replace_list:
            ori_content = ori_content.replace(rep[0], rep[1])
        return ori_content
