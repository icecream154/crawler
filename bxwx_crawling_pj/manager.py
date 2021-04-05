import concurrent
import concurrent.futures
from concurrent.futures.thread import ThreadPoolExecutor

from bxwx_crawling_pj.pipeline.task_initializer import TaskInitializer
from bxwx_crawling_pj.models.novel_task import BxwxNovelTask
from bxwx_crawling_pj.pipeline.content_fetcher import ContentFetcher
from bxwx_crawling_pj.pipeline.content_processor import ContentProcessor
from bxwx_crawling_pj.pipeline.data_saver import DataSaver
from bxwx_crawling_pj.utils.worker_pool import WorkerPool


def generate_novel_tasks(start: int, end: int):
    tasks = []
    for book_index in range(start, end + 1):
        tasks.append(BxwxNovelTask('https://www.bixiawenxue.org/book_' + str(book_index) + '/'))
    return tasks


if __name__ == '__main__':

    # init worker pools
    data_saver_worker_pool = WorkerPool(10, 100, DataSaver('/fakePath'))
    content_processor_worker_pool = WorkerPool(10, 100, ContentProcessor(data_saver_worker_pool))

    content_fetcher = ContentFetcher(None, content_processor_worker_pool)
    content_fetcher_worker_pool = WorkerPool(10, 100, content_fetcher)
    content_fetcher.content_fetcher_pool = content_fetcher_worker_pool

    task_initializer_worker_pool = WorkerPool(3, 10, TaskInitializer(content_fetcher_worker_pool))

    # start working
    data_saver_worker_pool.start_working()
    content_processor_worker_pool.start_working()
    content_fetcher_worker_pool.start_working()
    task_initializer_worker_pool.start_working()

    # submit tasks
    novel_tasks = generate_novel_tasks(1, 5)
    for task_id in range(len(novel_tasks)):
        task_initializer_worker_pool.submit(novel_tasks[task_id])

    # with ThreadPoolExecutor(max_workers=3) as init_pool, \
    #         ThreadPoolExecutor(max_workers=6) as content_fetcher_pool, \
    #         ThreadPoolExecutor(max_workers=6) as content_processor_pool, \
    #         ThreadPoolExecutor(max_workers=3) as data_saver_pool:
    #     data_saver = DataSaver('/fakePath')
    #     content_processor = ContentProcessor(data_saver_pool, data_saver)
    #     content_fetcher = ContentFetcher(content_fetcher_pool, content_processor_pool, content_processor)
    #     task_initializer = TaskInitializer(content_fetcher_pool, content_fetcher)
    #
    #     for novel_task_id in range(len(novel_tasks)):
    #         init_pool.submit(task_initializer, novel_tasks[novel_task_id])

