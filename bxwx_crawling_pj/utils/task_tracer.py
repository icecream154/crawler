from threading import Lock, RLock


class TaskTracer:
    """ A tracer to trace the situation of completion of some tasks

    You can register a list sub tracers when you initialize a tracer
    so that this tracer can automatically inform all sub tracers of the total
    number of sub tasks these sub tracers are tracing when all tasks traced by
    this tracer are done.
    
    Attributes:
        sub_task_tracer_list: list of sub tracers
        total_task_num: total number of tasks traced by this tracer
        done_task_num： number of current dealt tasks
        error_task_num: number of tasks that error occurs when worker is dealing the task
        child_task_num: number of child tasks
        _total_task_lock: lock that acquired immediately after initialized and only released when all tasks are done
        _modify_lock: lock required when modify these numbers

    """

    def __init__(self, sub_task_tracer_list: [] = [], total_task_num: int = None):
        """
        Tracer constructor
        A tracer can be initialized with default empty sub tracer list and unknown total task num

        :param sub_task_tracer_list: list of sub tracers
        :type sub_task_tracer_list: list
        :param total_task_num: total number of tasks traced by this tracer
        :type total_task_num: int
        """
        self.sub_task_tracer_list = sub_task_tracer_list
        self.total_task_num = total_task_num
        
        self.done_task_num = 0
        self.error_task_num = 0
        self.child_task_num = 0  # will be the total task num of sub tracers after all tasks are done
        
        self._total_task_lock = Lock()
        # acquire the total task lock immediately
        # lock is only released when all tasks are done and can be acquired again by all_done method
        self._total_task_lock.acquire()
        # modify lock should be locked when modify attributes and released after attributes modified
        self._modify_lock = Lock()

    def set_total_task_num(self, total_task_num: int):
        """
        total task num can be set by this method after tracer is initialized

        This method will judge whether all tasks are done immediately, otherwise
        _total_task_lock will never be released if all tasks are done before
        this method are called.

        :param total_task_num: total number of tasks traced by this tracer
        :type total_task_num: int
        """
        self.total_task_num = total_task_num
        if self.done_task_num + self.error_task_num == self.total_task_num:
            try:
                self._total_task_lock.release()
            except RuntimeError:
                """
                RuntimeError may occur because the following case is possible:
                (1) thread A execute [self.total_task_num = total_task_num] in method [set_total_task_num]
                (2) switch to thread B which has already executed [self.child_task_num += child_task_num]
                    in method[dealt]
                (3) thread B then execute the following if statement and got a True, so the lock is released
                    by thread B
                (4) switch back to A and the following if statement also got a True and the lock is released
                    again, thus a RuntimeError occurs because a lock can't be released before acquired
                this exception can be safely ignored 
                """
                print('release unlocked lock because lock is already released in dealt, safely ignore')

    def dealt(self, done_num: int = 0, error_num: int = 0, child_task_num: int = 0):
        """
        update done_task_num, error_task_num and child_task_num
        :param done_num: how many tasks are done by the worker
        :type done_num: int
        :param error_num: how many tasks find error occurs when worker is dealing the tasks
        :type error_num: int
        :param child_task_num: how many child tasks are submitted to downstream workers
        :type child_task_num: int
        """
        self._modify_lock.acquire()
        self.done_task_num += done_num
        self.error_task_num += error_num
        self.child_task_num += child_task_num
        if self.done_task_num is not None and self.done_task_num + self.error_task_num == self.total_task_num:
            try:
                self._total_task_lock.release()
            except RuntimeError:
                """
                reason why runtimeError may occur please read comments in method [set_total_task_num]
                """
                print('release unlocked lock because lock is already released in set_total_task_num, safely ignore')
        self._modify_lock.release()

    def all_done(self):
        """
        block until all tasks are done, if total task num is not set
        then all threads call this method will block forever
        :return: whether all tasks are dealt whatever success or failure, tricky bugs occur if this method return false
        :rtype: bool
        """
        self._total_task_lock.acquire()
        for sub_task_tracer in self.sub_task_tracer_list:
            sub_task_tracer.set_total_task_num(self.child_task_num)
        return self.done_task_num + self.error_task_num == self.total_task_num
