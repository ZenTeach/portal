import sys
import os
import unittest
import operator

from flask import url_for
from flask.cli import FlaskGroup
from flask_migrate import MigrateCommand
from server import create_app, db, bcrypt
from server.tests.factories import TeacherFactory, StudentFactory
from server.models import Student, Teacher, SchoolClass
import coverage
import datetime

app = create_app()
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

@cli.command('seed')
def seed():

    # Teacher seed
    password = bcrypt.generate_password_hash('Asdfgh12!')
    TeacherFactory.create(firstname="john", lastname="doe", email="john.doe@example.com", password=password.decode('utf-8'), role="Teacher")
    TeacherFactory.create(firstname="john", lastname="doe", email="john.doe+2@example.com", password=password.decode('utf-8'), role="Teacher")

    # Student
    StudentFactory.create(firstname="peter", lastname="griffin", email="peter.griffin@example.com", password=password.decode('utf-8'), role="Student")

    # SchoolClass
    class_student_id = Student.query.first().id
    class_teacher_id = Teacher.query.filter_by(role="Teacher").first().id
    SchoolClass(name="Algebra", subject="Math", start_date=datetime.date.today(), teacher_id=class_teacher_id, student_id=class_student_id).save()

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