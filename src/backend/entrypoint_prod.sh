#!/bin/sh

# Run migrations before booting up the app
python manage.py db upgrade

python manage.py db_conf

celery multi start worker1 \
    -A celery_worker.celery -l info

gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app
