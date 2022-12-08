#!/bin/sh

# TODO: switch to
# alembic upgrade head
python manage.py db upgrade

python manage.py db_conf
