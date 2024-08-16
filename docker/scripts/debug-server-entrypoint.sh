#!/bin/sh


until cd /app
do
    echo "Waiting for server volume..."
    sleep 1
done

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

poetry run python manage.py migrate --noinput
poetry run python manage.py create_default_groups
poetry run python manage.py runserver 0.0.0.0:80

exec "$@"