#!/bin/bash

NAME="Zenteach Background Processor - celery_start"

echo "Starting $NAME as `whoami`"

celery --app=celery_worker:celery worker \
        -B -l info --pidfile=/var/run/celery/%n.pid