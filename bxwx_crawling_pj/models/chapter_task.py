class ChapterTask:
    def __init__(self, chapter_id: int, book_identification: str, chapter_name: str, chapter_url: str):
        self.chapter_id = chapter_id
        self.book_identification = book_identification
        self.chapter_name = chapter_name
        self.chapter_url = chapter_url
        self.current_retry = 0
        self.max_retry = 2
