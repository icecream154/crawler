from bxwx_crawling_pj.models.task import AbstractTask


class BxwxNovelTask(AbstractTask):
    """ task dealt by ContentFetcher

    to find how many chapters this novel has and where to get these content

    Attributes:
        book_root_url: url of book's root page
    """

    def __init__(self, book_root_url: str):
        self.book_root_url = book_root_url
