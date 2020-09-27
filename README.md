# Zenteach Portal

## Prerequisites
- Download the latest [Python 3](https://www.python.org/)
- Download [PostgreSQL](https://www.postgresql.org/) version 12
- Install [Node.js](https://nodejs.org/en/download/)
- Install [Redis](https://redis.io/)
- Finally, install [Rabbitmq](https://www.rabbitmq.com/download.html)

## Setup
> ⚠️ **These commands were only tested on *nix like systems, please advise when running it on windows. It's advised tp use docker & docker-compose on windows.**

### Backend
The backend is a flask app written in python. `src/backend` contains all the backend code including models and apis. Copy the `.env.example` to `.env` and change these files.

#### Database setup
Project needs `zenteach` user in postgres. To create a user, run the following:

-
```bash
 createuser --interactive
 # Set the name to `zenteach` and grant super user privileges.
```

- Create the dev and test databases:
```
createdb -O zenteach zenteach_dev
createdb -O zenteach zenteach_test
```

- Next, we'll alter the database user password by logging in with

```bash
psql -U zenteach -d zenteach_dev
# Then execute
ALTER ROLE zenteach WITH PASSWORD 'zenteach';
```
This will set the password.

#### Rabbitmq setup

- Rabbitmq is a queue server used by `celery` the enqueue jobs. Together with Redis as the result backend, it serves as the background processing engine. For rabbitmq, we'd need to create a user `zenteach` and password `zenteach_broker` with admin privilege, please follow this [link](https://www.rabbitmq.com/access-control.html) to setup the users.

- We need a [vhost](https://www.rabbitmq.com/vhosts.html) for our jobs. Run the following command to add a vhost:

```bash
rabbitmqctl add_vhost jobs
```

### Running the backend

> :warning: **This command is only tested on *nix like systems, please advise when running it on windows. We advise using docker & docker-compose for windows.**

To run the backend server:

```bash
# install the deps first
pipenv install
env $(cat .env | xargs) ./entrypoint.sh init
```

**NOTE**: Please take a look at [Sample env file](#sample-env-file) for an example `.env` file.

### Frontend:

After installing node.js and npm, install [yarn](https://yarnpkg.com/) with `npm i -g yarn`.

- Copy the `.env.example` in the client source. No need to change this now.

- Then run the following in `client` to start the frontend dev server.

```
yarn install && yarn serve
```

Visit `localhost:8080`.


## Dockerized build

Both the backend and frontend have docker setups for local testing and development. Install [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/)

After installation run the following in the root folder to run the backend and frontend together:

```bash
pip install pre-commit && pre-commit install -c ../../.pre-commit-config.yaml
docker-compose up --build -d
```

This will download the prerequisites as docker images and run them in containers. Now you can access the frontend from `localhost:8080`.


## Sample env file

This is a sample env file to follow

```ini
FLASK_ENV=development
FLASK_ADMIN_SWATCH=journal
DATABASE_URL=postgres://zenteach:zenteach@localhost:5432/zenteach_dev
DATABASE_TEST_URL=postgres://zenteach:zenteach@localhost:5432/zenteach_test
APP_SETTINGS=server.config.DevelopmentConfig
CELERY_BROKER_URL=amqp://zenteach:zenteach_broker@localhost:5672/jobs
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/app
PYTHONUNBUFFERED=TRUE
PRECOMMIT_CONFIG=./src/backend/.pre-commit-config.yaml
```
