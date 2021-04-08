from bxwx_crawling_pj.models.task import AbstractTask


class ProcessTask(AbstractTask):
    def __init__(self, chapter_id: int, book_name: str, book_author: str, chapter_name: str, chapter_content: str):
        self.chapter_id = chapter_id
        self.book_name = book_name
        self.book_author = book_author
        self.book_identification = book_name + '-' + book_author
        self.chapter_name = chapter_name
        self.chapter_content = chapter_content
