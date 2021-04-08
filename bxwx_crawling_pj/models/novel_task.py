from bxwx_crawling_pj.models.task import AbstractTask


class BxwxNovelTask(AbstractTask):
    def __init__(self, book_root_url: str):
        self.book_root_url = book_root_url
