#!/bin/sh -e

VENVDIR=/var/www/zenteach_be/env
# reset PYTHONPATH
PYTHONPATH=$(which python)
FLASKDIR=/var/www/zenteach_be/
FLASK_REAL_LINK=$(readlink -f /var/www/zenteach_be/zenteach)
cd $VENVDIR
source bin/activate
export PYTHONPATH=$FLASK_REAL_LINK:$PYTHONPATH
export RUNTIME='production'

# Run migrations before booting up the app
cd $FLASKDIR/zenteach

pipenv sync

# _load_examboard in BaseConfig is called during import.
TMP_DIR="" python manage.py db upgrade
TMP_DIR="" python manage.py db_conf
