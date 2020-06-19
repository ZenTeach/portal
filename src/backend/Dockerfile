FROM python:3.7.5-slim-stretch

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" >> /etc/apt/sources.list.d/pgdg.list
RUN echo "deb http://deb.debian.org/debian stretch-backports main" >> /etc/apt/sources.list.d/sources.list

RUN apt-get update && \
	apt-get install -y build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi && \
	apt-get install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 && \
	apt-get install -y libgdk-pixbuf2.0-0 libffi-dev shared-mime-info && \
	apt-get install -y gfortran wget zlib1g zlib1g-dev && \
	apt-get install -y libfreetype6 libfreetype6-dev libpng-dev libopenblas-dev && \
	apt-get install -y netcat-openbsd libssl-dev python3-scipy libcurl4-openssl-dev python-pycurl && \
	apt-get install -y shared-mime-info libjpeg-dev fonts-open-sans

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt-get update && apt-get install -y libpq-dev

RUN mkdir -p /home/flask/server
WORKDIR /home/flask/server

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install pipenv

COPY Pipfile.* /home/flask/server/
RUN pipenv sync

COPY ./entrypoint.sh /home/flask/server/entrypoint.sh
RUN chmod +x /home/flask/server/entrypoint.sh

COPY . /home/flask/server

CMD ["/home/flask/server/entrypoint.sh"]
