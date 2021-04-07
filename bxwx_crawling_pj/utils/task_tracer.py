from threading import Lock, RLock


class TaskTracer:
    def __init__(self, sub_task_tracer_list: [] = [], total_task_num: int = None):
        self.sub_task_tracer_list = sub_task_tracer_list
        self.total_task_num = total_task_num
        self.total_task_lock = Lock()
        self.total_task_lock.acquire()
        self.modify_lock = Lock()
        self.done_task_num = 0
        self.error_task_num = 0
        self.child_task_num = 0

    def set_total_task_num(self, total_task_num: int):
        self.total_task_num = total_task_num
        if self.done_task_num + self.error_task_num == self.total_task_num:
            try:
                self.total_task_lock.release()
            except RuntimeError:
                print('release unlocked lock because lock is already released in dealt, safely ignore')

    def dealt(self, done_num: int = 0, error_num: int = 0, child_task_num: int = 0):
        self.modify_lock.acquire()
        self.done_task_num += done_num
        self.error_task_num += error_num
        self.child_task_num += child_task_num
        if self.done_task_num + self.error_task_num == self.total_task_num:
            try:
                self.total_task_lock.release()
            except RuntimeError:
                print('release unlocked lock because lock is already released in set_total_task_num, safely ignore')
        self.modify_lock.release()

    def all_done(self):
        self.total_task_lock.acquire()
        for sub_task_tracer in self.sub_task_tracer_list:
            sub_task_tracer.set_total_task_num(self.child_task_num)
        return self.done_task_num + self.error_task_num == self.total_task_num
