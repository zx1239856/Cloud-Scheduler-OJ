#!/bin/bash

nginx
python manage.py migrate
python manage.py loaddata database.json
# python manage.py runserver 0.0.0.0:8000
gunicorn api.wsgi -k gevent -b 0.0.0.0:8000 -D --access-logfile - --log-level info
daphne api.asgi:application --bind 0.0.0.0 --port 8001
