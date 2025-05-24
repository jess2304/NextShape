#!/usr/bin/env bash

HOST_PORT=$1
shift

HOST=$(echo $HOST_PORT | cut -d: -f1)
PORT=$(echo $HOST_PORT | cut -d: -f2)

echo "Waiting for DataBase for $HOST:$PORT..."

while ! nc -z $HOST $PORT; do
  sleep 0.5
done

echo "The DataBase is ready."
exec "$@"
