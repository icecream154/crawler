import requests
from bs4 import BeautifulSoup

from bxwx_crawling_pj.pipeline.task_worker import TaskWorker
from bxwx_crawling_pj.utils.task_tracer import TaskTracer
from bxwx_crawling_pj.utils.worker_pool import WorkerPool
from bxwx_crawling_pj.models.novel_task import BxwxNovelTask
from bxwx_crawling_pj.models.fetch_task import FetchTask


class TaskInitializer(TaskWorker):

    def __init__(self, content_fetcher_pool: WorkerPool, task_tracer: TaskTracer = None):
        self.content_fetcher_pool = content_fetcher_pool
        self.task_tracer = task_tracer

    def deal_task(self, novel_task: BxwxNovelTask):
        try:
            book_root_url = novel_task.book_root_url
            html_text = requests.get(book_root_url).text
            phrase_soup = BeautifulSoup(html_text, 'lxml')
            book_name = TaskInitializer._get_book_name(phrase_soup)
            book_author = TaskInitializer._get_author_name(phrase_soup)
            book_identification = book_name + '-' + book_author
            chapter_num = self._submit_resource_fetch_task(phrase_soup, book_root_url, book_name, book_author)
            if self.task_tracer is not None:
                self.task_tracer.dealt(done_num=1, child_task_num=chapter_num)
            print('task [%s] submit success' % book_identification)
        except Exception as ex:
            print(ex)
            print("task [%s] submit failed" % book_root_url)
            if self.task_tracer is not None:
                self.task_tracer.dealt(error_num=1)

    @staticmethod
    def _get_book_name(phrase_soup):
        book_meta_data = phrase_soup.find('div', id='info').h1.text.split(' / ')
        book_name = book_meta_data[0]
        return book_name

    @staticmethod
    def _get_author_name(phrase_soup):
        book_meta_data = phrase_soup.find('div', id='info').h1.text.split(' / ')
        book_author = book_meta_data[1]
        return book_author

    def _submit_resource_fetch_task(self, phrase_soup, book_root_url: str, book_name: str, book_author: str):
        # find all chapters
        chapter_list_dl = phrase_soup.find('dl', class_='zjlist')
        curr_chapter_id = 0
        for chapter_dd in chapter_list_dl.find_all('dd'):
            chapter_link = chapter_dd.a
            if chapter_link is not None:
                # update current chapter id
                curr_chapter_id += 1
                # add relative url to the root url and phrase the html text
                chapter_url = book_root_url + chapter_dd.a.get('href')
                self.content_fetcher_pool.submit(FetchTask(curr_chapter_id, book_name, book_author,
                                                           chapter_link.text, chapter_url)
                                                 )
        return curr_chapter_id
