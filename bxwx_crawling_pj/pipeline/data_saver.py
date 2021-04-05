from bxwx_crawling_pj.models.save_task import SaveTask


class DataSaver:

    def __init__(self, save_path: str):
        self.save_path = save_path

    def __call__(self, save_task: SaveTask):
        print('cid:[%d] - chapter [%s] of book [%s] saved in [%s]' %
              (save_task.chapter_id, save_task.chapter_name, save_task.book_identification, self.save_path))
        print('content [%s] ...' % save_task.processed_chapter_content[0: 15])
