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
fi

pipenv run python manage.py seed

pipenv run celery multi start worker1 \
    -A celery_worker.celery -B -l info

pipenv run python manage.py run -h 0.0.0.0

trap "Killing celery workers" SIGINT

ps auxww | awk '/celery worker/ {print $2}' | xargs kill -9
