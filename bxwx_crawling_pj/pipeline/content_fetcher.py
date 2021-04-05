import requests

from bxwx_crawling_pj.models.chapter_task import ChapterTask
from bxwx_crawling_pj.models.process_task import ProcessTask
from bxwx_crawling_pj.pipeline.content_processor import ContentProcessor
from concurrent.futures import ThreadPoolExecutor


class ContentFetcher:
    def __init__(self, content_fetcher_pool: ThreadPoolExecutor,
                 content_processor_pool: ThreadPoolExecutor, content_processor: ContentProcessor):
        self.content_fetcher_pool = content_fetcher_pool
        self.content_processor_pool = content_processor_pool
        self.content_processor = content_processor

    @staticmethod
    def get_html_text(url, timeout=12):
        return requests.get(url, timeout=timeout).text

    def __call__(self, chapter_task: ChapterTask):
        try:
            self.content_processor_pool.submit(self.content_processor,
                                               ProcessTask(chapter_task.chapter_id, chapter_task.book_identification,
                                                           chapter_task.chapter_name,
                                                           ContentFetcher.get_html_text(chapter_task.chapter_url))
                                               )
        except Exception as ex:
            print('content [%s] fetch failed ...' % chapter_task.chapter_url)
            chapter_task.current_retry += 1
            if chapter_task.current_retry <= chapter_task.max_retry:
                self.content_fetcher_pool.submit(self, chapter_task)
