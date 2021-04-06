from bxwx_crawling_pj.utils.task_tracer import TaskTracer
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


# global task tracer
novel_task_tracer = None
chapter_task_tracer = None

if __name__ == '__main__':

    # init worker pools
    # data_saver
    data_saver = DataSaver('/fakePath')
    data_saver_worker_pool = WorkerPool(10, 1000, data_saver)

    # content_processor
    content_processor =  ContentProcessor(data_saver_worker_pool)
    content_processor_worker_pool = WorkerPool(10, 1000, content_processor)

    # content_fetcher
    content_fetcher = ContentFetcher(None, content_processor_worker_pool)
    content_fetcher_worker_pool = WorkerPool(400, 1000, content_fetcher)
    content_fetcher.content_fetcher_pool = content_fetcher_worker_pool

    # task_initializer
    task_initializer = TaskInitializer(content_fetcher_worker_pool)
    task_initializer_worker_pool = WorkerPool(20, 100, task_initializer)

    # submit tasks
    novel_tasks = generate_novel_tasks(51, 70)
    # record how many novel tasks
    global novel_task_tracer
    novel_task_tracer = TaskTracer(len(novel_tasks))
    task_initializer.register_tracer(novel_task_tracer)

    for task_id in range(task_initializer_worker_pool.task_pool.max_capacity
                         if task_initializer_worker_pool.task_pool.max_capacity < len(novel_tasks)
                         else len(novel_tasks)):
        task_initializer_worker_pool.submit(novel_tasks[task_id])

    # start working
    task_initializer_worker_pool.start_working()
    data_saver_worker_pool.start_working()
    content_processor_worker_pool.start_working()
    content_fetcher_worker_pool.start_working()

    if len(novel_tasks) > task_initializer_worker_pool.task_pool.max_capacity:
        for task_id in range(task_initializer_worker_pool.task_pool.max_capacity, len(novel_tasks)):
            task_initializer_worker_pool.submit(novel_tasks[task_id])

    if novel_task_tracer.all_done():
        print('all novel tasks init success，all chapter task %d', novel_task_tracer.child_task_num)


