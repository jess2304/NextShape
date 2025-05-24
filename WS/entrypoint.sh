#!/bin/sh

# Stop on error
set -e

echo "ENV = $ENV"

./wait.sh $DATABASE_HOST:$DATABASE_PORT -- echo "PostgreSQL DataBase is ready."

# Apply migrations
echo "Apply the migrations"
python manage.py migrate

if [ "$ENV" = "dev" ]; then
    echo "Development mode"
    exec python manage.py runserver 0.0.0.0:8000
elif [ "$ENV" = "test" ]; then
    echo "Testing mode"
    exec pytest --disable-warnings --cov=api
elif [ "$ENV" = "test" ]; then
    echo "Production mode"
    exec gunicorn next_shape_ws.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
else
    echo "Unknown ENV : $ENV"
    exit 1
fi
