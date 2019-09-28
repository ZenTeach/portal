import datetime
import json

from server import db


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


class BaseModelMixin(object):
    """ Abstract class adding common functionalities """

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        filtered_columns = list(
            filter(lambda x: x not in self.filterable_columns, self.__table__.columns))
        model_hash = {c.name: getattr(self, c.name)
                      for c in filtered_columns}
        return json.loads(json.dumps(model_hash, default=myconverter))
