#!/bin/bash
docker pull postgres
mkdir -p $HOME/docker/volumes/postgres_zenteach
docker run --rm  --name pg-docker -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v $HOME/docker/volumes/postgres_zenteach:/var/lib/postgresql/data_zenteach postgres
sleep 5
PGPASSWORD=docker createdb -h localhost -p 5432 -U postgres zenteachDB
