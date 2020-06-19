
from server import db


class BaseModelMixin(object):
    """ Abstract class adding common functionalities """

    def save(self):
        db.session.add(self)
        db.session.commit()
