#!/bin/bash

echo "Collecting statics"
python manage.py collectstatic --noinput

echo "Migrating database"
python manage.py migrate

echo "Starting server"
python manage.py runserver 0.0.0.0:5002