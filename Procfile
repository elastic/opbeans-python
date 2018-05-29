web: gunicorn -b 0.0.0.0:8000 opbeans.wsgi
tasks: celery -A opbeans -c 1 worker -l info
beat: celery -A opbeans beat -l info
load: molotov --delay 0.6 molotov_scenarios.py
