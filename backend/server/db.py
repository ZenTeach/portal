"""Plain-SQLAlchemy compatibility shim.

Replicates the subset of the Flask-SQLAlchemy extension API that the server
models and services actually use, without requiring a Flask application
object. This lets the same model layer serve both the legacy Flask app and
the FastAPI app.

Supported surface (mirrors ``flask_sqlalchemy.SQLAlchemy``):

* ``db.Model`` -- declarative base with a per-class ``query`` descriptor that
  honors each model's ``query_class``, plus automatic ``__tablename__``
  generation (``CamelCase`` -> ``snake_case``).
* ``db.session`` -- scoped session.
* ``db.relationship`` / ``db.backref`` -- relationships defaulting to
  ``query_class=BaseQuery`` so ``lazy="dynamic"`` relationships and
  ``BaseModelMixin.to_dict`` keep working.
* ``db.engine`` / ``db.get_engine()`` -- the Engine (created lazily from
  ``SQLALCHEMY_DATABASE_URI``).
* ``db.create_all()`` / ``db.drop_all()``.
* Column helpers via ``db.Column``, ``db.Integer``, ... (delegated to
  ``sqlalchemy`` / ``sqlalchemy.orm``).
"""

import os
import re
import threading
from contextvars import ContextVar

import sqlalchemy as sa
from flask_sqlalchemy import BaseQuery
from sqlalchemy import create_engine, event
from sqlalchemy.orm import (Query, Session, backref, declarative_base,
                            relationship as orm_relationship, scoped_session,
                            sessionmaker)
from sqlalchemy.pool import Pool


# Per-request session scope for the FastAPI path.  When set (by the
# ``get_db_session`` dependency) the scoped session resolves to a session
# owned by the current request regardless of the worker thread a sync route
# executes on.  When unset the registry falls back to thread-local scope,
# which is exactly what the legacy Flask path expects.
_request_session_scope = ContextVar("db_request_session_scope", default=None)


def _session_scope():
    scope = _request_session_scope.get()
    if scope is not None:
        return scope
    return threading.get_ident()


def _enter_request_session():
    """Bind a fresh request-scoped session to the registry.

    Returns the session plus the contextvar token needed by
    :func:`_exit_request_session`.  Called on the event-loop thread; worker
    threads running sync route handlers inherit the scope via the copied
    context, so ``db.session`` resolves to this same session everywhere.
    """
    scope = object()
    token = _request_session_scope.set(scope)
    # Ensure the session factory is bound to the engine before the scoped
    # session is materialized (the engine is otherwise created lazily, and a
    # session created before that would have no bind configured).
    db.engine
    return db.session(), token


def _exit_request_session(token):
    """Remove the request-scoped session and restore the previous scope."""
    db.session.remove()
    _request_session_scope.reset(token)


async def get_db_session():
    """FastAPI dependency yielding a request-scoped ``db.session``.

    The scope token makes ``db.session`` resolve to the same session on the
    event-loop thread (where this dependency sets up and tears down) and on
    any worker thread a sync route handler runs on.  The session is removed
    after the request, so connection/transaction resources are released.
    """
    session, token = _enter_request_session()
    try:
        yield session
    finally:
        _exit_request_session(token)


def _camel_to_snake_case(name):
    """Convert a ``CamelCase`` name to ``snake_case``."""
    name = re.sub(r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))", r"_\1", name)
    return name.lower().lstrip("_")


def _should_set_tablename(cls):
    """Determine whether ``__tablename__`` should be generated for a model.

    Mirrors ``flask_sqlalchemy.model.should_set_tablename``.
    """
    if cls.__dict__.get("__abstract__", False) or not any(
        isinstance(b, sa.orm.DeclarativeMeta) for b in cls.__mro__[1:]
    ):
        return False

    for base in cls.__mro__:
        if "__tablename__" not in base.__dict__:
            continue

        if isinstance(base.__dict__["__tablename__"], sa.orm.declared_attr):
            return False

        return not (
            base is cls
            or base.__dict__.get("__abstract__", False)
            or not isinstance(base, sa.orm.DeclarativeMeta)
        )

    return True


class _NameMetaMixin(type):
    """Metaclass mixin that sets a model's ``__tablename__``.

    Mirrors ``flask_sqlalchemy.model.NameMetaMixin``.
    """

    def __init__(cls, name, bases, d, **kwargs):
        if _should_set_tablename(cls):
            cls.__tablename__ = _camel_to_snake_case(cls.__name__)

        super().__init__(name, bases, d, **kwargs)

        if (
            "__tablename__" not in cls.__dict__
            and "__table__" in cls.__dict__
            and cls.__dict__["__table__"] is None
        ):
            del cls.__table__

    def __table_cls__(cls, *args, **kwargs):
        """Called by SQLAlchemy during mapper setup."""
        schema = kwargs.get("schema")
        key = args[0] if schema is None else f"{schema}.{args[0]}"

        if key in cls.metadata.tables:
            return sa.Table(*args, **kwargs)

        for arg in args:
            if (isinstance(arg, sa.Column) and arg.primary_key) or isinstance(
                arg, sa.PrimaryKeyConstraint
            ):
                return sa.Table(*args, **kwargs)

        for base in cls.__mro__[1:-1]:
            if "__table__" in base.__dict__:
                break
        else:
            return sa.Table(*args, **kwargs)

        if "__tablename__" in cls.__dict__:
            del cls.__tablename__

        return None


class _DefaultMeta(_NameMetaMixin, sa.orm.DeclarativeMeta):
    """SQLAlchemy declarative metaclass that provides ``__tablename__`` support."""


class Model:
    """Base class for all models. Subclass ``db.Model`` (not this)."""

    query_class = BaseQuery
    query = None  # set by the extension after the declarative base is built

    def __repr__(self):
        state = sa.inspect(self)
        if state.transient:
            pk = f"(transient {id(self)})"
        elif state.pending:
            pk = f"(pending {id(self)})"
        else:
            pk = ", ".join(map(str, state.identity))
        return f"<{type(self).__name__} {pk}>"


class _QueryProperty:
    """Class property creating a ``query`` object for a model."""

    def __init__(self, db):
        self._db = db

    def __get__(self, obj, cls):
        query_class = getattr(cls, "query_class", BaseQuery)
        return query_class(cls, session=self._db.session())


class _SQLAlchemyCompat:
    """Minimal drop-in for the Flask-SQLAlchemy extension singleton."""

    def __init__(self):
        self.metadata = sa.MetaData()
        self.Model = declarative_base(
            metadata=self.metadata,
            cls=Model,
            name="Model",
            metaclass=_DefaultMeta,
        )
        self.Model.query_class = BaseQuery
        self.Model.query = _QueryProperty(self)
        self.Model.__fsa__ = self

        self._app = None
        self._uri = None
        self._engine = None
        self._session_factory = sessionmaker(
            class_=Session,
            query_cls=BaseQuery,
        )
        self.session = scoped_session(self._session_factory, scopefunc=_session_scope)

        @event.listens_for(Pool, "checkout")
        def _ping_connection(dbapi_connection, connection_record, connection_proxy):
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("SELECT 1;")
            except Exception as exc:
                connection_proxy._pool.dispose()
                raise exc.DisconnectionError()
            cursor.close()

    # -- lifecycle ---------------------------------------------------------

    def init_app(self, app=None, uri=None):
        """Bind to a Flask app (legacy path) or an explicit URI (FastAPI path).

        When bound to a Flask app, the URI is resolved lazily from the app's
        current ``SQLALCHEMY_DATABASE_URI`` config so config overrides applied
        after init (e.g. tests switching to ``TestingConfig``) are honored.
        """
        if uri is not None:
            self._uri = uri
        if app is not None:
            self._app = app
        self._reset_engine()
        return self

    def _resolve_uri(self):
        if self._uri:
            return self._uri
        if self._app is not None:
            uri = self._app.config.get("SQLALCHEMY_DATABASE_URI")
            if uri:
                return uri
        return os.environ.get("DATABASE_URL")

    def _reset_engine(self):
        if self._engine is not None:
            try:
                self._engine.dispose()
            except Exception:
                pass
        self._engine = None

    # -- engine / session --------------------------------------------------

    @property
    def engine(self):
        if self._engine is None:
            uri = self._resolve_uri()
            if not uri:
                raise RuntimeError(
                    "No SQLAlchemy database URI configured. Set DATABASE_URL "
                    "or pass uri= to db.init_app()."
                )
            self._engine = create_engine(uri)
            self._session_factory.configure(bind=self._engine)
        return self._engine

    def get_engine(self, bind=None, bind_key=None):
        return self.engine

    # -- DDL ---------------------------------------------------------------

    def create_all(self, bind=None):
        self.metadata.create_all(bind=bind or self.engine)

    def drop_all(self, bind=None):
        self.metadata.drop_all(bind=bind or self.engine)

    def configure_mappers(self):
        from sqlalchemy.orm import configure_mappers

        configure_mappers()

    # -- relationship helpers ----------------------------------------------

    def relationship(self, *args, **kwargs):
        kwargs.setdefault("query_class", BaseQuery)
        if "backref" in kwargs:
            backref_ = kwargs["backref"]
            if isinstance(backref_, str):
                backref_ = (backref_, {})
            backref_[1].setdefault("query_class", BaseQuery)
        return orm_relationship(*args, **kwargs)

    def dynamic_loader(self, argument, **kwargs):
        return self.relationship(argument, lazy="dynamic", **kwargs)

    # -- attribute fallthrough ---------------------------------------------

    def __getattr__(self, name):
        import sqlalchemy.orm as sa_orm

        if name == "event":
            return event
        if name == "backref":
            return backref
        for module in (sa, sa_orm):
            if hasattr(module, name):
                return getattr(module, name)
        raise AttributeError(
            "{!r} object has no attribute {!r}".format(
                self.__class__.__name__, name
            )
        )


db = _SQLAlchemyCompat()
"""Shared SQLAlchemy compatibility instance used by models and services."""
