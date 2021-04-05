from abc import ABC, abstractmethod


class AbstractBookCrawler(ABC):

    def __init__(self, book_root_url: str, save_path='./'):
        self.book_root_url = book_root_url
        self.save_path = save_path

    @staticmethod
    def get_book_name(phrase_soup):
        pass

    @staticmethod
    def get_author_name(phrase_soup):
        pass

    @staticmethod
    def get_chapter_list(phrase_soup, book_root_url):
        pass

    @abstractmethod
    def crawl_chapter(self, start_c_id: int, end_c_id: int):
        pass

    @abstractmethod
    def save_chapter(self, c_id, save_file):
        pass
