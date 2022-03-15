
import json
import logging
from typing import Optional
from uuid import UUID, uuid4

from server import db
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy_utils import Timestamp

logger = logging.getLogger(__name__)


class BaseModelMixin(Timestamp):
    """ Abstract class adding common functionalities """
    _IGNORED_COLUMNS = []

    def to_dict(self, show=None, _hide=[], _path=None):
        """Return a dictionary representation of this model."""

        show = show or []

        hidden = self._hidden_fields if hasattr(self, "_hidden_fields") else []
        default = self._default_fields if hasattr(self, "_default_fields") else []
        default.extend(['id', 'updated', 'created'])

        if not _path:
            _path = self.__tablename__.lower()

            def prepend_path(item):
                item = item.lower()
                if item.split(".", 1)[0] == _path:
                    return item
                if len(item) == 0:
                    return item
                if item[0] != ".":
                    item = f".{item}"
                item = f"{_path}{item}"
                return item

            _hide[:] = [prepend_path(x) for x in _hide]
            show[:] = [prepend_path(x) for x in show]

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        properties = dir(self)

        ret_data = {}

        for key in columns:
            if key.startswith("_"):
                continue
            check = f"{_path}.{key}"
            if check in _hide or key in hidden:
                continue
            if check in show or key in default:
                ret_data[key] = getattr(self, key)

        for key in relationships:
            if key.startswith("_"):
                continue
            check = f"{_path}.{key}"
            if check in _hide or key in hidden:
                continue
            if check in show or key in default:
                _hide.append(check)
                is_list = self.__mapper__.relationships[key].uselist
                if is_list:
                    items = getattr(self, key)
                    if self.__mapper__.relationships[key].query_class is not None:
                        if hasattr(items, "all"):
                            items = items.all()
                    ret_data[key] = []
                    for item in items:
                        ret_data[key].append(
                            item.to_dict(
                                show=list(show),
                                _hide=list(_hide),
                                _path=f"{_path}.{key.lower()}",
                            )
                        )
                else:
                    if (
                        self.__mapper__.relationships[key].query_class is not None
                        or self.__mapper__.relationships[key].instrument_class
                        is not None
                    ):
                        item = getattr(self, key)
                        if item is not None:
                            ret_data[key] = item.to_dict(
                                show=list(show),
                                _hide=list(_hide),
                                _path=(f"{_path}.{key.lower()}"),
                            )
                        else:
                            ret_data[key] = None
                    else:
                        ret_data[key] = getattr(self, key)

        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith("_"):
                continue
            if not hasattr(self.__class__, key):
                continue
            attr = getattr(self.__class__, key)
            if not (isinstance(attr, property) or isinstance(attr, QueryableAttribute)):
                continue
            check = f"{_path}.{key}"
            if check in _hide or key in hidden:
                continue
            if check in show or key in default:
                val = getattr(self, key)
                if hasattr(val, "to_dict"):
                    ret_data[key] = val.to_dict(
                        show=list(show),
                        _hide=list(_hide), _path=f"{_path}.{key.lower()}"
                    )
                else:
                    try:
                        ret_data[key] = json.loads(json.dumps(val))
                    except:  # nosec  # noqa: E722
                        pass

        return ret_data

    def save(self, refresh=False):
        db.session.add(self)
        db.session.commit()

        if refresh:
            db.session.refresh(self)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def reload(self):
        db.session.refresh(self)

    def update_and_save(self, **kwargs: dict) -> None:
        """
            update_and_save

            Updates the model from a dictionary and save it in db.
        """
        for item, value in kwargs.items():
            if hasattr(self, item) and item not in self._IGNORED_COLUMNS:
                self.__setattr__(item, value)

        self.save(refresh=kwargs.get('refresh', False))

    def __iter__(self):
        table = self.__table__
        for key in table.columns.keys():
            if key not in table.primary_key and key not in self._IGNORED_COLUMNS:
                yield(key, getattr(self, key))


def unique_uuid4(x: Optional[UUID] = None) -> UUID:
    if x is None:
        x = uuid4()
    return x
