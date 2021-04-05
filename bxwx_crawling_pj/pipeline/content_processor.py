from bxwx_crawling_pj.models.process_task import ProcessTask
from bxwx_crawling_pj.models.save_task import SaveTask
from bxwx_crawling_pj.pipeline.data_saver import DataSaver
from concurrent.futures import ThreadPoolExecutor


class ContentProcessor:

    def __init__(self, data_saver_pool: ThreadPoolExecutor, data_saver: DataSaver):
        self.data_saver_pool = data_saver_pool
        self.data_saver = data_saver

    def __call__(self, process_task: ProcessTask):
        book_name = process_task.book_identification.split('-')[0]
        self.data_saver_pool.submit(self.data_saver,
                                    SaveTask(process_task.chapter_id, process_task.book_identification,
                                             process_task.chapter_name,
                                             ContentProcessor._process_content(book_name, process_task.chapter_content))
                                    )

    @staticmethod
    def _process_content(book_name: str, chapter_content: str):
        replace_list = [('    ', '\n    '),
                        ('笔下文学网 www.bixiawenxue.org，最快更新' + book_name + '最新章节！', '\n')]
        filtered_content = ContentProcessor._content_filter(chapter_content, replace_list)
        return filtered_content

    @staticmethod
    def _content_filter(ori_content: str, replace_list: [(str, str)]):
        for rep in replace_list:
            ori_content = ori_content.replace(rep[0], rep[1])
        return ori_content
