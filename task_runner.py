import json
from queue import Empty, Queue
from threading import Thread, Event
import time
import os

class ThreadPool:
    def __init__(self):
        if os.getenv('TP_NUM_OF_THREADS'):
            self.THREAD_COUNT = int(os.getenv('TP_NUM_OF_THREADS'))
        else:
            self.THREAD_COUNT = os.cpu_count()

        self.task_queue: Queue[dict] = Queue()

        self.threads = []
        for _ in range(self.THREAD_COUNT):
            task_runner = TaskRunner(self.task_queue)
            task_runner.start()
            self.threads.append(task_runner)

    def add_task(self, task):
        self.task_queue.put(task)

    def stop(self):
        for thread in self.threads:
            thread.stop()

class TaskRunner(Thread):
    def __init__(self, task_queue: Queue[dict]):
        super().__init__()
        self.running = True
        self.tasK_queue = task_queue

    def stop(self):
        self.running = False

    def __write_status(self, job_id: int, data: dict | None = None):
        with open(f'app/results/{job_id}', 'w') as f:
            if data:
                f.write(json.dumps({'status': 'done', 'data': data}))
            else:
                f.write(json.dumps({'status': 'running'}))

    def run(self):
        while self.running:
            try:
                task = self.tasK_queue.get(block=False)
                job_id, data, f = task['job_id'], task['data'], task['f']

                self.__write_status(job_id)
                ret = f(*data)
                self.__write_status(job_id, ret)
            except Empty:
                continue