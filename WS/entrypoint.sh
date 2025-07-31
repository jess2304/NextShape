#!/usr/bin/env bash

echo "ENV = $ENV"

# Check if cert is mounted and update it
if [ -n "$BREVO_PEM" ]; then
  echo -e "$BREVO_PEM" > /usr/local/share/ca-certificates/brevo.crt
  echo "Brevo certificate was detected — update-ca-certificates"
  update-ca-certificates
else
  echo "No Brevo certificate detected."
fi

./wait.sh "$DATABASE_HOST:$DATABASE_PORT"

# Apply migrations
echo "Apply the migrations"
python manage.py migrate

echo "Collect static files"
python manage.py collectstatic --noinput

if [ "$ENV" = "local" ]; then
    echo "Local mode (Docker local)"
    echo "Seeding the database..."
    python manage.py seed || echo "Seeding failed or already done"
    exec python manage.py runserver 0.0.0.0:8000
elif [ "$ENV" = "dev"  ]; then
    echo "Development mode"
    echo "Seeding the database..."
    python manage.py seed || echo "Seeding failed or already done"
    exec python manage.py runserver 0.0.0.0:8000
elif [ "$ENV" = "test" ]; then
    echo "Testing mode"
    exec pytest --disable-warnings --cov=api
elif [ "$ENV" = "prod" ]; then
    echo "Production mode"
    exec gunicorn next_shape_ws.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
else
    echo "Unknown ENV : $ENV"
    exit 1
fi
