class SaveTask:
    def __init__(self, chapter_id: int, book_identification: str, chapter_name: str, processed_chapter_content: str):
        self.chapter_id = chapter_id
        self.book_identification = book_identification
        self.chapter_name = chapter_name
        self.processed_chapter_content = processed_chapter_content
