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
    python manage.py seed
fi


celery multi start worker1 \
    -A celery_worker.celery -B -l DEBUG \
    --pidfile=tmp/pid/celery/%n.pid \
    -f tmp/celery-worker.log info

celery -A celery_worker.celery beat -S redbeat.RedBeatScheduler -l DEBUG -f tmp/celery-beat.log --detach --max-interval 60

gunicorn 'wsgi:app' -b 127.0.0.1:5000 --workers 1 \
  --worker-class aiohttp.GunicornWebWorker \
  --log-level info \
  --access-logfile tmp/development.log \
  --error-logfile tmp/development.log \
  -p tmp/pid/server.pid \
  --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"' \

trap "Killing python workers" SIGINT

ps auxww | awk '/python/ {print $2}' | xargs sudo kill -9
