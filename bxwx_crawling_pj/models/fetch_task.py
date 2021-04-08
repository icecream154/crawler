from bxwx_crawling_pj.models.task import AbstractTask


class FetchTask(AbstractTask):
    """ task dealt by ContentFetcher

    to fetch content from the web with certain url

    Attributes:
        chapter_id: chapter index of the content in the book
        book_name: novel name
        book_author: author of the novel
        chapter_name: title of the chapter
        chapter_url: url to fetch chapter content
    """

    def __init__(self, chapter_id: int, book_name: str, book_author: str, chapter_name: str, chapter_url: str):
        self.chapter_id = chapter_id
        self.book_name = book_name
        self.book_author = book_author
        self.book_identification = book_name + '-' + book_author
        self.chapter_name = chapter_name
        self.chapter_url = chapter_url
        self.current_retry = 0
        self.max_retry = 2
