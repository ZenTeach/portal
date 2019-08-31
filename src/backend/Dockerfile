FROM python:3.7.2-alpine

RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev && \
    apk add postgresql-dev && \
    apk add netcat-openbsd && \
    apk add libffi-dev

RUN mkdir -p /home/flask/server
WORKDIR /home/flask/server

COPY ./requirements.txt /home/flask/server/requirements.txt
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /home/flask/server/entrypoint.sh
RUN chmod +x /home/flask/server/entrypoint.sh

COPY . /home/flask/server

CMD ["/home/flask/server/entrypoint.sh"]