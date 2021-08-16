import json
import logging
import os
from functools import lru_cache
from typing import List

from flask import current_app, session
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import current_user
from flask_wtf.csrf import _FlaskFormCSRF
from jinja2 import Markup
from server.config import _load_examboard
from server.models import QuestionChoice
from wtforms.meta import DefaultMeta

logger = logging.getLogger('admin::view')


def report_5xx_error(exception: Exception):
    sentry_dsn_key = os.environ.get("SENTRY_DSN")
    from sentry_sdk import capture_exception, init
    init(sentry_dsn_key)
    capture_exception(exception)


@lru_cache(64)
def _loaded_examboard() -> List:
    return list(_load_examboard().get('exam_board').items())


class CustomSecureForm(SecureForm):
    class Meta(DefaultMeta):
        csrf_class = _FlaskFormCSRF
        csrf_context = session

        @property
        def csrf_secret(self):
            return current_app.\
                config.\
                get("WTF_CSRF_SECRET_KEY",
                    current_app.secret_key)

        @property
        def csrf_time_limit(self):
            return current_app.config.get("WTF_CSRF_TIME_LIMIT", 3600)


class BaseView(ModelView):
    can_export = True
    list_template = "admin/list.html"
    create_template = "admin/create.html"
    edit_template = "admin/edit.html"
    form_base_class = CustomSecureForm

    def is_accessible(self):
        return current_user.is_authenticated


def json_formatter(view, context, model, name):
    value = getattr(model, name)
    json_value = json.dumps(value, ensure_ascii=False, indent=2)
    return Markup("<pre>{}</pre>".format(json_value))


def date_format(view, context, model, name):
    value = getattr(model, name)
    return value.strftime("%Y-%m-%d")


def exam_board_formatter(view, context, model, name):
    value = getattr(model, name)
    boards = _loaded_examboard()
    filtered = list(
        filter(lambda x: x[0] == value, boards)
    )
    if len(filtered) == 0:
        return ''
    else:
        return filtered[0][1]


def subject_formatter(view, context, model, name):
    if model.subject is not None:
        return model.subject.name
    else:
        return ''


def correct_choice_formatter(view, context, model, name):
    value = getattr(model, name)
    choice = QuestionChoice.query.filter_by(id=value).first()
    if choice:
        return choice.value
    else:
        return ""
