import datetime
import operator
import os
import sys
import pytest

import coverage
import sqlalchemy as sa
from flask import url_for
from flask.cli import FlaskGroup
from flask_migrate import MigrateCommand
from server import bcrypt, create_app, db

app = create_app(False)
cli = FlaskGroup(create_app=create_app)
cli.add_command('db', MigrateCommand)

COV = coverage.coverage(
    branch=True,
    include='server/*',
    omit=[
        'server/tests/*',
        'server/config.py',
    ]
)
COV.start()


@cli.command('recreate_db')
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command('db_conf')
def db_conf():
    sa.orm.configure_mappers()


@cli.command()
def test():
    """Runs the tests without code coverage"""
    pytest.main(["-s", "server/tests"])


@cli.command('routes')
def routes():
    """ Prints all registered routes"""
    print("Method \tEndpoint \turl name")
    for rule in app.url_map.iter_rules():
        # url = url_for(rule.endpoint, **(rule.defaults or {}))
        #method = [(http_method in ['GET', 'POST']) for http_method in sorted(rule.methods)].join(',')
        print("{} \t{} \t{}".format(rule.methods, rule.endpoint, str(rule)))


@cli.command('seed')
def seed():
    from server.models import run_seed
    run_seed()


@cli.command('coverage')
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('server/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    sys.exit(result)


if __name__ == '__main__':
    cli()
