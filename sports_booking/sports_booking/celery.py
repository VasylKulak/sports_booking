# from __future__ import absolute_import, unicode_literals
# import os
# import django
# from celery import Celery
# from django.conf import settings
#
# # Set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sports_booking.settings')
#
# # Ensure Django is fully set up before starting Celery
# django.setup()
#
# # Initialize Celery app
# app = Celery('sports_booking')
#
# # Load configuration from Django settings
# app.config_from_object('django.conf:settings', namespace='CELERY')
#
# # Auto-discover tasks from all installed apps
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
#
# # Optional: Add a test task to confirm Celery is working
# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
