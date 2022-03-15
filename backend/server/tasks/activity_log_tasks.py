from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class SummarizerTask:
    def __init__(self, task_id, task_name, task_args, task_kwargs):
        self.task_id = task_id
        self.task_name = task_name
        self.task_args = task_args
        self.task_kwargs = task_kwargs

    def __call__(self):
        pass
