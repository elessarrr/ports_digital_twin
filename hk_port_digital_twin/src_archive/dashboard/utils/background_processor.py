import threading
import queue

class BackgroundProcessor:
    """
    A class to handle background data processing tasks.
    """
    def __init__(self):
        self.task_queue = queue.Queue()
        self.results = {}
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def _worker(self):
        """
        The worker thread that processes tasks from the queue.
        """
        while True:
            task_id, task, args, kwargs = self.task_queue.get()
            try:
                result = task(*args, **kwargs)
                self.results[task_id] = {"status": "completed", "result": result}
            except Exception as e:
                self.results[task_id] = {"status": "failed", "error": str(e)}
            self.task_queue.task_done()

    def add_task(self, task, *args, **kwargs):
        """
        Adds a task to the processing queue.
        """
        task_id = len(self.results)
        self.results[task_id] = {"status": "pending"}
        self.task_queue.put((task_id, task, args, kwargs))
        return task_id

    def get_result(self, task_id):
        """
        Gets the result of a task.
        """
        return self.results.get(task_id)