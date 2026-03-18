#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r greenloop_backend/requirements.txt
python greenloop_backend/manage.py collectstatic --noinput
python greenloop_backend/manage.py migrate
