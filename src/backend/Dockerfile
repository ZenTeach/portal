FROM python:3.7.2-alpine

RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories

RUN apk update && \
	apk add --virtual build-deps gcc python-dev musl-dev && \
	apk add gfortran py-pip build-base wget && \
	apk add freetype-dev libpng-dev openblas-dev && \
	apk add alpine-sdk && \
	apk add postgresql-dev && \
	apk add netcat-openbsd && \
	apk add libffi-dev && \
	apk add openssl-dev && \
	apk add zlib zlib-dev && \
	apk add py3-cffi && \
	apk add cairo-dev && \
	apk add pango-dev && \
	apk add gdk-pixbuf && \
	apk add shared-mime-info jpeg-dev && \
	apk add ttf-opensans

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN mkdir -p /home/flask/server
WORKDIR /home/flask/server

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /home/flask/server/requirements.txt
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /home/flask/server/entrypoint.sh
RUN chmod +x /home/flask/server/entrypoint.sh

COPY . /home/flask/server

CMD ["/home/flask/server/entrypoint.sh"]
