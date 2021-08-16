web: gunicorn app:flask_app
worker: celery -A app:flask_app worker -l INFO
