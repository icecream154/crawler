import requests

from bxwx_crawling_pj.models.chapter_task import ChapterTask
from bxwx_crawling_pj.models.process_task import ProcessTask
from bxwx_crawling_pj.pipeline.content_processor import ContentProcessor
from bxwx_crawling_pj.utils.worker_pool import WorkerPool


class ContentFetcher:
    def __init__(self, content_fetcher_pool: WorkerPool,
                 content_processor_pool: WorkerPool):
        self.content_fetcher_pool = content_fetcher_pool
        self.content_processor_pool = content_processor_pool

    @staticmethod
    def get_html_text(url, timeout=12):
        return requests.get(url, timeout=timeout).text

    def deal_task(self, chapter_task: ChapterTask):
        try:
            self.content_processor_pool.submit(ProcessTask(chapter_task.chapter_id, chapter_task.book_identification,
                                                           chapter_task.chapter_name,
                                                           ContentFetcher.get_html_text(chapter_task.chapter_url))
                                               )
        except Exception as ex:
            print('content [%s] fetch failed ...' % chapter_task.chapter_url)
            chapter_task.current_retry += 1
            if chapter_task.current_retry <= chapter_task.max_retry:
                self.content_fetcher_pool.submit(chapter_task)
