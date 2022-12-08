#!/bin/sh

gunicorn 'wsgi:app' -b 127.0.0.1:5000 --workers 1 \
  --worker-class aiohttp.GunicornWebWorker \
  --log-level info \
  --access-logfile tmp/development.log \
  --error-logfile tmp/development.log \
  -p tmp/pid/server.pid \
  --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"' \
