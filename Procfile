web: gunicorn --workers 4 --bind 0.0.0.0:3000 opbeans.wsgi
tasks: celery -A opbeans worker --concurrency=1 -l info
beat: celery -A opbeans beat -l info
