from __future__ import absolute_import, unicode_literals

#from celery import task
from celery.utils.log import get_task_logger

from django.core.mail import send_mail, BadHeaderError
from ComplianceReporting.settings import EMAIL_HOST_USER
from django.conf import settings

from celery import Celery
import datetime
import celery
from django.contrib.auth.decorators import *
from app.models import *
from user_auth.models import *

from celery import shared_task
app = Celery('ComplianceReporting', broker='pyamqp://guest@localhost//')

logger = get_task_logger(__name__)


@shared_task(name='send_email_task',bind=True)
def send_email_task(to, subject, message):
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


@app.task(name='send_reminder_email_task')
def send_reminder_email_task():
    if datetime.now().month-1 == 12:
        year = datetime.now().year-1
    else:
        year = datetime.now().year

    subject = 'Compliance Reporting Reminder'
    message = "Hi, This is a polite reminder to submit your monthly compliance report. Click this link to continue"
    #get contractors who have not created an entry
    unreported_contractors = User.objects.filter(is_contractor=True, is_active=True)

     #get entries
    entries = ComplianceRecordEntry.objects.filter(month=datetime.now().month-1,year=year,is_active=True).values('last_updated_by')

    #get contractors who have created entry but not submitted
    for contractor in unreported_contractors:
        if contractor not in entries:
            #send reminder to submit report
            #logger.info(f"from={EMAIL_HOST_USER}, {to=}, {subject=}, {message=}")
    
            try:
                logger.info("About to send_mail")
                #send_mail(subject, message, EMAIL_HOST_USER, [to])
                send_mail(
                        subject,
                        message,
                        EMAIL_HOST_USER,
                        [contractor.email],
                        fail_silently=False,
                    )
                logger.info("I think email has been sent")
            except BadHeaderError:
                logger.info("BadHeaderError")
            except Exception as e:
                logger.error(e)
    #send message
    pass


@shared_task(name='adding_task')
def adding_task(x, y):
    return x + y

@shared_task(name='myTask')
def myTask():
    # Do something here
    # like accessing remote apis,
    # calculating resource intensive computational data
    # and store in cache
    # or anything you please
    logger.info("Chal nadi")
    print(f"Chal nadi!!")
    return 'Chal nadi'


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
