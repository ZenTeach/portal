# syntax = docker/dockerfile:1.2
FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential libpq-dev libffi-dev \
        libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 shared-mime-info \
        libjpeg-dev zlib1g-dev libopenblas-dev \
        libcurl4-openssl-dev fonts-open-sans \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/flask/server

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/home/flask/server
ENV PROMETHEUS_MULTIPROC_DIR=/tmp

COPY ./requirements.txt /home/flask/server/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./entrypoint.sh /home/flask/server/entrypoint.sh
COPY ./pre-start.sh /home/flask/server/pre-start.sh
RUN chmod +x /home/flask/server/entrypoint.sh /home/flask/server/pre-start.sh

COPY . /home/flask/server

EXPOSE 5000
CMD ["/home/flask/server/pre-start.sh"]
ENTRYPOINT ["/home/flask/server/entrypoint.sh"]
