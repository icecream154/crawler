import os
import sys

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


if __name__ == '__main__':

    # init worker pools
    # data_saver
    data_saver_tracer = TaskTracer()
    data_saver = DataSaver('/fakePath', data_saver_tracer)
    data_saver_worker_pool = WorkerPool(20, 1000, data_saver, is_daemon=True)

    # content_processor
    content_processor_tracer = TaskTracer([data_saver_tracer])
    content_processor = ContentProcessor(data_saver_worker_pool, content_processor_tracer)
    content_processor_worker_pool = WorkerPool(40, 2000, content_processor, is_daemon=True)

    # content_fetcher
    content_fetcher_tracer = TaskTracer([content_processor_tracer])
    content_fetcher = ContentFetcher(None, content_processor_worker_pool, content_fetcher_tracer)
    content_fetcher_worker_pool = WorkerPool(600, 2000, content_fetcher, is_daemon=True)
    content_fetcher.content_fetcher_pool = content_fetcher_worker_pool

    # task_initializer
    task_initializer_tracer = TaskTracer([content_fetcher_tracer])
    task_initializer = TaskInitializer(content_fetcher_worker_pool, task_initializer_tracer)
    task_initializer_worker_pool = WorkerPool(20, 100, task_initializer, is_daemon=True)

    # submit tasks
    novel_tasks = generate_novel_tasks(101, 120)
    task_initializer.task_tracer.set_total_task_num(len(novel_tasks))

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

    if task_initializer_tracer.all_done():
        print('novel tasks [%d] done and [%d] failed，fetch tasks %d submitted' %
              (task_initializer_tracer.done_task_num, task_initializer_tracer.error_task_num,
               task_initializer_tracer.child_task_num))

    if content_fetcher_tracer.all_done():
        print('fetch tasks [%d] done and [%d] failed，process tasks %d submitted' %
              (content_fetcher_tracer.done_task_num, content_fetcher_tracer.error_task_num,
               content_fetcher_tracer.child_task_num))

    if content_processor_tracer.all_done():
        print('process tasks [%d] done and [%d] failed，data tasks %d submitted' %
              (content_processor_tracer.done_task_num, content_processor_tracer.error_task_num,
               content_processor_tracer.child_task_num))

    if data_saver_tracer.all_done():
        print('all data saving tasks [%d] done' % data_saver_tracer.done_task_num)

    sys.exit(0)
