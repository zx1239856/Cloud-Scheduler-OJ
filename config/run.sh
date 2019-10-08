#!/bin/bash

nginx

python manage.py migrate
# python manage.py runserver 0.0.0.0:8000
gunicorn 'api.wsgi' -k gevent -b 0.0.0.0:8000 --access-logfile - --log-level info

