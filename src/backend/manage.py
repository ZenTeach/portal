import sys
# import unittest

from flask.cli import FlaskGroup

from server import create_app, db
# from app.api.models import Teacher, Student

app = create_app()
cli = FlaskGroup(create_app=create_app)

@cli.command('recreate_db')
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    cli()