import os
from celery.schedules import crontab

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','')
#SQLALCHEMY_DATABASE_URI = 'sqlite:///./flaskr.db'
# To instance/config.py
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
# import os
# os.urandom(24)
SECRET_KEY = '\xdcb#\xe2.\xbf4\xebHo\x85.\xcf\x9c\x1b\xbfR\xa5\x1e\xf1\x99.}^'
# To instance/config.py
#DEBUG = True
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = 'Asia/Tokyo'
CELERY_BROKER_URL = os.environ.get('REDIS_URL','')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL','')
CELERYBEAT_SCHEDULE = {
    'destroy_workrecs': {
        'task': 'flaskr.jobs.destroy_workrec',
        'schedule': crontab(hour=1,minute=0)
    }
}