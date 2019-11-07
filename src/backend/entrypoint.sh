#!/bin/sh


echo "Waiting for postgres..."

while ! nc -z zenteach_db 5432; do
    sleep 0.1
done

echo "PostgreSQL started"

# Run migrations before booting up the app
python manage.py db upgrade

python manage.py db_conf

python manage.py seed

python manage.py run -h 0.0.0.0
