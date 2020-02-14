#!/bin/sh -e

VENVDIR=/var/www/zenteach_be/env
FLASKDIR=/var/www/zenteach_be/

cd $VENVDIR
source bin/activate
export PYTHONPATH=$FLASKDIR/zenteach:$FLASKDIR:$PYTHONPATH

# Run migrations before booting up the app
cd $FLASKDIR/zenteach
pip install -r requirements.txt

python manage.py db upgrade

python manage.py db_conf

celery multi start worker1 \
    -A celery_worker.celery -l info
