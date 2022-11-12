#!/bin/bash

echo "Collecting statics"
python manage.py collectstatic --noinput

echo "Migrating database"
python manage.py migrate

echo "Starting server"
hypercorn hitomi_client.asgi:application 0.0.0.0:5003