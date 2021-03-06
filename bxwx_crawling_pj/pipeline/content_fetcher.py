import requests

from bxwx_crawling_pj.models.fetch_task import FetchTask
from bxwx_crawling_pj.models.process_task import ProcessTask
from bxwx_crawling_pj.pipeline.task_worker import TaskWorker
from bxwx_crawling_pj.utils.task_tracer import TaskTracer
from bxwx_crawling_pj.utils.worker_pool import WorkerPool


class ContentFetcher(TaskWorker):
    def __init__(self, content_fetcher_pool: WorkerPool,
                 content_processor_pool: WorkerPool, task_tracer: TaskTracer = None):
        self.content_fetcher_pool = content_fetcher_pool
        self.content_processor_pool = content_processor_pool
        self.task_tracer = task_tracer

    @staticmethod
    def get_html_text(url, timeout=30):
        return requests.get(url, timeout=timeout).text

    def deal_task(self, chapter_task: FetchTask):
        try:
            self.content_processor_pool.submit(ProcessTask(chapter_task.chapter_id, chapter_task.book_name,
                                                           chapter_task.book_author, chapter_task.chapter_name,
                                                           ContentFetcher.get_html_text(chapter_task.chapter_url))
                                               )
            if self.task_tracer is not None:
                self.task_tracer.dealt(done_num=1, error_num=0, child_task_num=1)
        except Exception as ex:
            print('content [%s] fetch failed caused by [%s] ...' % (chapter_task.chapter_url, str(ex)[:20]))
            chapter_task.current_retry += 1
            if chapter_task.current_retry <= chapter_task.max_retry:
                print('retry ...')
                self.content_fetcher_pool.submit(chapter_task)
            else:
                print('too many retries ...')
                self.task_tracer.dealt(done_num=0, error_num=1, child_task_num=0)  # one error and no sub task generated
