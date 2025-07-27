#!/usr/bin/env bash
set -e

echo "ENV = $ENV"

./wait.sh "$DATABASE_HOST:$DATABASE_PORT"

echo "Apply the migrations"
python manage.py migrate

case "$ENV" in
  dev)
    echo "Seeding database..."
    python manage.py seed || echo "Seeding failed or already done"
    exec python manage.py runserver 0.0.0.0:8000
    ;;
  test)
    exec pytest --disable-warnings --cov=api
    ;;
  prod)
    exec gunicorn next_shape_ws.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
    ;;
  *)
    echo "Unknown ENV: $ENV"
    exit 1
    ;;
esac
