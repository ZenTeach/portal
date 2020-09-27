#!/bin/sh


echo "Waiting for postgres..."

while ! nc -z localhost 5432; do
    sleep 0.1
done

echo "PostgreSQL started"

python manage.py db upgrade

python manage.py db_conf

pre-commit install -c $PRECOMMIT_CONFIG

# Run migrations before booting up the app
if [[ "$1" == "init" ]] ;then
    echo "Deleting database schema"
    python manage.py truncate_tables
fi

python manage.py seed

celery multi start worker1 \
    -A celery_worker.celery -B -l info

python manage.py run -h 0.0.0.0

trap "Killing celery workers" SIGINT

ps auxww | awk '/celery worker/ {print $2}' | xargs kill -9
