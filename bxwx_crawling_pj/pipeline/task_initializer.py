import requests
from bs4 import BeautifulSoup

from bxwx_crawling_pj.models.novel_task import BxwxNovelTask
from bxwx_crawling_pj.models.chapter_task import ChapterTask
from bxwx_crawling_pj.pipeline.content_fetcher import ContentFetcher
from concurrent.futures import ThreadPoolExecutor


class TaskInitializer:
    def __init__(self, content_fetcher_pool: ThreadPoolExecutor, content_fetcher: ContentFetcher):
        self.content_fetcher_pool = content_fetcher_pool
        self.content_fetcher = content_fetcher

    def __call__(self, novel_task: BxwxNovelTask):
        try:
            book_root_url = novel_task.book_root_url
            html_text = requests.get(book_root_url).text
            phrase_soup = BeautifulSoup(html_text, 'lxml')
            book_name = TaskInitializer._get_book_name(phrase_soup)
            book_author = TaskInitializer._get_author_name(phrase_soup)
            book_identification = book_name + '-' + book_author
            self._submit_resource_fetch_task(phrase_soup, book_root_url, book_identification)
            print('task [%s] submit success' % book_identification)
        except Exception as ex:
            print(ex)
            print("task [%s] submit failed" % book_root_url)

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

    def _submit_resource_fetch_task(self, phrase_soup, book_root_url, book_identification):
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
                self.content_fetcher_pool.submit(self.content_fetcher,
                                                 ChapterTask(curr_chapter_id, book_identification,
                                                             chapter_link.text, chapter_url)
                                                 )
