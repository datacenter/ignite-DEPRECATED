#from __future__ import absolute_import
# Django starts so that shared_task will use this app.
#import celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ignite.settings')
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery_tasks import app as celery_app  # noqa
