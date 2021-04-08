from bxwx_crawling_pj.models.task import AbstractTask


class ChapterTask(AbstractTask):
    def __init__(self, chapter_id: int, book_name: str, book_author: str, chapter_name: str, chapter_url: str):
        self.chapter_id = chapter_id
        self.book_name = book_name
        self.book_author = book_author
        self.book_identification = book_name + '-' + book_author
        self.chapter_name = chapter_name
        self.chapter_url = chapter_url
        self.current_retry = 0
        self.max_retry = 2
