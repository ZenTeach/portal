#!/bin/sh

NAME="api_server"
SOCKFILE=/run/server_sock
NUM_WORKERS=5
HOST=127.0.0.1
PORT=5000

gunicorn 'wsgi:app' -b $HOST:$PORT \
  --name $NAME \
  --workers $NUM_WORKERS \
	--worker-class aiohttp.GunicornWebWorker \
	--worker-connections 1000 \
  --log-level info \
  --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"' \
  --bind=unix:$SOCKFILE 
