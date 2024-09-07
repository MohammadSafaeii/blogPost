from __future__ import absolute_import, unicode_literals
import os
from celery.schedules import crontab
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogSite.settings')

app = Celery('blogSite')

# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# can handle this cronjob in django admin
app.conf.beat_schedule = {
    'create-rating-bins-every-day': {
        'task': 'blogs.tasks.updating_blogs_process',
        'schedule': crontab(hour='0', minute='0'),  # Runs every day
    },
}
