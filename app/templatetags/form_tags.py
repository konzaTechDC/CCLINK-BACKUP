from django import template
from app.models import *
from app.forms import *
from django.contrib.auth.forms import PasswordChangeForm

register = template.Library()

@register.simple_tag
def get_personnel_designation_form():
    form = PersonnelDesignationForm()
    return form

@register.simple_tag
def get_password_change_form(user):
    form = PasswordChangeForm(user)
    return form

@register.simple_tag
def set_default_reminder_message(request):
    contractors = User.objects.filter(is_projectmanager=True, is_active=True)
    subject = 'Reminder of Compliance Report Submission'
    days_left = 10 - datetime.now().day
    message = 'kindly note that you have ' +str(days_left)+ ' days to submit your monthly compliance report.'

    context={
        'contractors':contractors,
        'subject':subject,
        'days_left':days_left,
        'message':message
        }

    return context