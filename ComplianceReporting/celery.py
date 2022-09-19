from __future__ import absolute_import
import os

from celery import Celery
from celery import shared_task
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ComplianceReporting.settings')

#app = Celery('ComplianceReporting', broker='redis://guest@127.0.0.1:6379')
app = Celery('ComplianceReporting',backend=settings.CELERY_RESULT_BACKEND, broker='pyamqp://guest@localhost//')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['ComplianceReporting'])



app.conf.beat_schedule = {
    #Scheduler Name
    'print-message-ten-seconds': {
        # Task Name (Name Specified in Decorator)
        'task': 'myTask',  
        # Schedule      
        'schedule': 10.0,
        # Function Arguments 
       # 'args': ("Hello",) 
    },
  #  'print-time-twenty-seconds': {
  #      # Task Name (Name Specified in Decorator)
  #      'task': 'send_email_task',  
  #      # Schedule      
  #      'schedule': 20.0,
  #      # Function Arguments 
  #      'args': ('enyaluogo@konza.go.ke','Testing','Chal nadi',) 
  #  },
    'send-email-twentyfour-hours': {
        # Task Name (Name Specified in Decorator)
        'task': 'send_reminder_email_task',  
        # Schedule      
        'schedule': 86400.0,
        # Function Arguments 
        #'args': ('enyaluogo@konza.go.ke','Testing','Chal nadi',) 
    },
    
} 

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@app.task(name='send_mail_not',bind=True)
def send_mail_not(to, subject, message):
    logger.info(f"from={EMAIL_HOST_USER}, {to}, {subject}, {message}")
    
    try:
        logger.info("About to send_mail")
        #send_mail(subject, message, EMAIL_HOST_USER, [to])
        send_mail(
                subject,
                message,
                EMAIL_HOST_USER,
                [EMAIL_HOST_USER, to],
                fail_silently=False,
            )
        logger.info("I think email has been sent")
    except BadHeaderError:
        logger.info("BadHeaderError")
    except Exception as e:
        logger.error(e)
