from django import template
from app.models import *
from datetime import datetime

register = template.Library()

@register.simple_tag
def get_form_date():
    month = datetime.now().month-1
    if month == 0:
        month = 12
        year = datetime.now().year-1
    else:
        year = datetime.now().year

    
    if month == 1:
        month = 'January'
    elif month == 2:
        month = 'February'
    elif month is 3:
        month = 'March'
    elif month == 4:
        month = 'April'
    elif month == 5:
        month = 'May'
    elif month is 6:
        month = 'June'
    elif month is 7:
        month = 'July'
    elif month is 8:
        month = 'August'
    elif month is 9:
        month = 'September'
    elif month is 10:
        month = 'October'
    elif month is 11:
        month = 'November'
    elif month is 12:
        month = 'December'
    else:
        month = 'Undated'

    month_year = {
        'month':month,
        'year':year,}
    return month_year

@register.simple_tag
def is_submission_period():

    current_date = datetime.now().day

    if current_date < 10:
        return True
    else:
        return False


@register.simple_tag
def contractor_has_sent_for_this_month(record, user):

    #check if an entry has already been sent
    try:

    #check if contractor has already subitted a report
        if datetime.now().month-1 == 0:
            check_entry = ComplianceRecordEntry.objects.get(compliance_record=record, month=12, year=datetime.now().year-1, submitted_by = user, is_deleted=False, is_active=True,status='pending')
        else:
            check_entry = ComplianceRecordEntry.objects.get(compliance_record=record, month=datetime.now().month-1, year=datetime.now().year, submitted_by = user, is_deleted=False, is_active=True,status='pending')

        return check_entry
                
    except:
        try:

        #check if contractor has already subitted a report and evaluated
            if datetime.now().month-1 == 0:
                check_entry = ComplianceRecordEntry.objects.get(compliance_record=record, month=12, year=datetime.now().year-1, submitted_by = user, is_deleted=False, is_active=True,status='rejected')
            else:
                check_entry = ComplianceRecordEntry.objects.get(compliance_record=record, month=datetime.now().month-1, year=datetime.now().year, submitted_by = user, is_deleted=False, is_active=True,status='rejected')

            return check_entry
                
        except:
            return False

@register.simple_tag
def get_this_month_submissions():
  
    #check if contractor has already subitted a report
    if datetime.now().month-1 == 0:
        check_entry = ComplianceRecordEntry.objects.filter( month=12, year=datetime.now().year-1, is_deleted=False, is_active=True)
    else:
        check_entry = ComplianceRecordEntry.objects.filter( month=datetime.now().month-1, year=datetime.now().year,  is_deleted=False, is_active=True)

    return check_entry
    