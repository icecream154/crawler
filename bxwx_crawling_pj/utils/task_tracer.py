from threading import Lock, RLock


class TaskTracer:
    def __init__(self, total_task_num):
        self.total_task_num = total_task_num
        self.total_task_lock = Lock()
        self.total_task_lock.acquire()
        self.modify_lock = Lock()
        self.done_task_num = 0
        self.child_task_num = 0

    def dealt(self, dealt_num: int, child_task_num: int = 0):
        self.modify_lock.acquire()
        self.done_task_num += dealt_num
        self.child_task_num += child_task_num
        if self.done_task_num == self.total_task_num:
            self.total_task_lock.release()
        self.modify_lock.release()

    def all_done(self):
        self.total_task_lock.acquire()
        return self.done_task_num == self.total_task_num
