#!/bin/bash

NAME="Zenteach Background Processor - worker-start"

PROJECT_DIR=$(cd - && pwd)
SOURCEDIR=$(readlink -f $PROJECT_DIR)
CONFIG_FILE="{{ flaskapp_app_directory }}/application.cfg"


echo "Starting $NAME as `whoami`"

export PYTHONPATH=$PROJECT_DIR:$SOURCEDIR:$PYTHONPATH
export FLASK_ENV="production"
export TEMPLATE_DIR=$SOURCEDIR/server/templates

# Activate the virtual environment
cd "${PROJECT_DIR}"


celery --app=celery_worker:celery worker \
        -l info --pidfile=/var/run/celery/%n.pid
