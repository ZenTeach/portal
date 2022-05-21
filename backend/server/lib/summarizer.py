from collections import namedtuple
from datetime import datetime, timedelta
from typing import List, NamedTuple

import pandas as pd
from celery.utils.log import get_task_logger
from inflection import humanize, pluralize, titleize
from server.models import ActivityLog, Teacher
from sqlalchemy import Date, cast

logger = get_task_logger(__name__)

# ds -- data namedtuple
Log: NamedTuple = namedtuple(
    'Log',
    ['actor_id', 'action', 'item_type', 'item_id'])

EVENTS = {
    'daily': ['quiz_grade', 'class_quiz'],
    'week': ['class_quiz', 'school_class'],
    'month': ['topics', 'knowledge_items', 'invitations', 'questions']
}


class EmptyLogException(Exception):
    pass


class Summarizer(object):
    crosstab = None
    _all_event: dict = EVENTS

    def __init__(self, teacher: Teacher):
        self.teacher = teacher
        self.logs: List[Log] = []
        self.mode: str = ''

    def __call__(self, interval: int) -> None:
        try:
            self.get_logs_by_temporal_grouping(interval)
            self.get_crosstab_from_dims()
            self.generate_human_friendly_summary()
        except EmptyLogException:
            print(f"Got empty logs for user {self.teacher}")
            return

    @property
    def processed_logs(self) -> List[Log]:
        return self.logs

    @property
    def processed_crosstab(self) -> pd.DataFrame:
        return self.crosstab

    # Step 1: We first get a collection of logs grouped by a certain date interval.
    def get_logs_by_temporal_grouping(self, n_interval_ago: int) -> None:
        """
            Get the logs from n_interval_ago.
        """
        if n_interval_ago > 30 and n_interval_ago < 1:
            logger.exception(f'Unrecognized time interval: {n_interval_ago}')
            raise Exception(f'Unrecognized time interval: {n_interval_ago}')

        if n_interval_ago == 30:
            self.mode = 'month'
        elif n_interval_ago == 7:
            self.mode = 'week'
        else:
            self.mode = 'daily'

        interval_delta = datetime.now() - timedelta(days=n_interval_ago)
        activity_logs = self._construct_query(self.teacher, interval_delta)

        if len(activity_logs) == 0:
            raise EmptyLogException()

        for log in activity_logs:
            self.logs.append(Log(log.actor_id, log.action, log.item_type, log.item_id))

    def _construct_query(self, teacher: Teacher, delta):
        # get event types
        events = self._all_event[self.mode]
        logs = ActivityLog.query\
            .filter(ActivityLog.actor == teacher,
                    ActivityLog.item_type.in_(events),
                    cast(ActivityLog.created, Date) < delta).all()
        return logs

    # Step 2: Compute the cross-tabulation of the logs. Dimensions are action and item_type
    def get_crosstab_from_dims(self):
        dims = ['action', 'item_type']
        df = pd.DataFrame(self.logs)
        self.crosstab = pd.crosstab(df[dims[0]], df[dims[1]])

    # Step 3: Generate human-friendly note.
    def generate_human_friendly_summary(self) -> None:
        """
        Generate human-friendly summary. And store it in ActivityLog.
        """
        # Created 10 School classes
        template = "{} {} {}"
        crosstab_dict = self.crosstab.to_dict()
        for item in crosstab_dict:
            action, count = zip(*crosstab_dict[item].items())
            # convert from tuple to str
            action = action[0]
            count = count[0]
            if count > 2:
                ActivityLog(
                    actor=self.teacher,
                    action=action,
                    item_type=f"summarize_{item}",
                    item_id=0,
                    note=template.format(titleize(action+'d'), count, pluralize(humanize(item)))
                ).save()
