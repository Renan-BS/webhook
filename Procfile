web: gunicorn app:flask_app
worker: celery -A celery_app.celery --loglevel=info --pool=solo
