#!/bin/bash
python manage.py makemigrations
python manage.py migrate

python manage.py makemigrations healthnet
python manage.py migrate healthnet

