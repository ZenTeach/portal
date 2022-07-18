#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z zenteach_db 5432; do
    sleep 3
done

echo "PostgreSQL started"

pipenv run python manage.py db upgrade

pipenv run python manage.py db_conf

# Run migrations before booting up the app
if [[ "$1" == "init" ]] ;then
    echo "Deleting database schema"
    pipenv run python manage.py truncate_tables
    pipenv run python manage.py seed
fi


pipenv run celery multi start worker1 \
    -A celery_worker.celery -B -l DEBUG \
    --pidfile=tmp/pid/celery/%n.pid \
    -f tmp/celery-worker.log info


pipenv run celery -A celery_worker.celery beat \
    -S redbeat.RedBeatScheduler -l DEBUG \
    -f tmp/celery-beat.log \
    --detach --max-interval 60
pipenv run python manage.py run -h 0.0.0.0

trap "Killing celery workers" SIGINT

ps auxww | awk '/celery worker/ {print $2}' | xargs kill -9
