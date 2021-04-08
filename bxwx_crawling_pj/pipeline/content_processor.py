from bs4 import BeautifulSoup

from bxwx_crawling_pj.models.process_task import ProcessTask
from bxwx_crawling_pj.models.save_task import SaveTask
from bxwx_crawling_pj.pipeline.task_worker import TaskWorker
from bxwx_crawling_pj.utils.worker_pool import WorkerPool
from bxwx_crawling_pj.utils.task_tracer import TaskTracer


class ContentProcessor(TaskWorker):

    def __init__(self, data_saver_pool: WorkerPool, task_tracer: TaskTracer = None):
        self.data_saver_pool = data_saver_pool
        self.task_tracer = task_tracer

    def done_task(self):
        pass

    def deal_task(self, process_task: ProcessTask):
        book_name = process_task.book_identification.split('-')[0]
        processed_content = ContentProcessor._process_content(book_name, process_task.chapter_content)
        if processed_content is not None:
            self.data_saver_pool.submit(SaveTask(process_task.chapter_id, process_task.book_name,
                                                 process_task.book_author, process_task.chapter_name, processed_content)
                                        )
            if self.task_tracer is not None:
                self.task_tracer.dealt(done_num=1, child_task_num=1)
        else:
            if self.task_tracer is not None:
                self.task_tracer.dealt(error_num=1)

    @staticmethod
    def _process_content(book_name: str, chapter_content: str):
        chapter_html_phrase_soup = BeautifulSoup(chapter_content, 'lxml')

        # find the div with content of the novel
        content_div = chapter_html_phrase_soup.find('div', id='content')
        if content_div is None:
            print('cid [%d] chapter content not found')
            return None
        replace_list = [('    ', '\n    '),
                        ('笔下文学网 www.bixiawenxue.org，最快更新' + book_name + '最新章节！', '\n')]
        filtered_content = ContentProcessor._content_filter(content_div.text, replace_list)
        return filtered_content

    @staticmethod
    def _content_filter(ori_content: str, replace_list: [(str, str)]):
        for rep in replace_list:
            ori_content = ori_content.replace(rep[0], rep[1])
        return ori_content
