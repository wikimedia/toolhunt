#!/bin/bash
/data/project/toolhunt-api/www/python/venv/bin/celery -A app.celery worker --loglevel=info
