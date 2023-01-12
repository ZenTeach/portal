#!/bin/sh

gunicorn 'wsgi:app' -b 127.0.0.1:5000 --workers 1 \
 --worker-class aiohttp.GunicornWebWorker \
 --log-level info \
 --access-logfile tmp/development.log \
 --error-logfile tmp/development.log \
 -p tmp/pid/server.pid \
 --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"' \

celery -A celery_worker.celery \
    worker -B -l INFO \
    --scheduler=redbeat.RedBeatScheduler \
    --pidfile=tmp/pid/celery/%n.pid \
    -f tmp/celery-worker.log

trap "Killing python workers" SIGTERM

ps auxww | grep -E '(gunicorn|celery)' | awk '{print $2}' | xargs sudo kill -9
