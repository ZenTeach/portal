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


class Summarizer(object):
    crosstab = None

    def __init__(self, teacher: Teacher):
        self.teacher = teacher
        self.logs: List[Log] = []

    def __call__(self):
        pass

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

        interval_delta = datetime.now() - timedelta(days=n_interval_ago)
        activity_logs = ActivityLog.query\
            .filter(ActivityLog.actor == self.teacher,
                    cast(ActivityLog.created, Date) < interval_delta).all()

        for log in activity_logs:
            self.logs.append(Log(log.actor_id, log.action, log.item_type, log.item_id))

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
