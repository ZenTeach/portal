import sys
import os
import unittest
import operator

from flask import url_for
from flask.cli import FlaskGroup
from flask_migrate import MigrateCommand
from server import create_app, db

app = create_app()
cli = FlaskGroup(create_app=create_app)
cli.add_command('db', MigrateCommand)

@cli.command('recreate_db')
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command()
def test():
    """Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('server/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    sys.exit(result)

@cli.command('routes')
def routes():
    """ Prints all registered routes"""
    print("Method \tEndpoint \turl name")
    for rule in app.url_map.iter_rules():
        # url = url_for(rule.endpoint, **(rule.defaults or {}))
        #method = [(http_method in ['GET', 'POST']) for http_method in sorted(rule.methods)].join(',')
        print("{} \t{} \t{}".format(rule.methods, rule.endpoint, str(rule)))
if __name__ == '__main__':
    cli()