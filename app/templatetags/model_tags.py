from django import template
from app.models import *
from app.compliance_context_preprocessors import *

register = template.Library()

#get previously submitted entries
@register.simple_tag
def get_previous_entries(request):
    entries = ComplianceRecordEntry.objects.filter(created_by=request.user,is_deleted=False,is_active=True,is_published=True).order_by('-id') or None

    if not entries:
        return None
    else:
        return entries

#check if reports are related
@register.simple_tag
def get_relationship( curr_entry):
    try:
        relationship = EntryInheritance.objects.get(child=curr_entry)
        return relationship
    except:
        return None

#get metric issues
@register.simple_tag
def get_requirement_issue(entry, requirement):
    try:
        issue = ComplianceRequirementIssue.objects.get(entry=entry,requirement=requirement,is_deleted=False)
        return issue
    except:
        return None


#get personnel issues
@register.simple_tag
def get_personnel_issue(entry, personnel_designation):
    try:
        personnel = Personnel.objects.get(record_entry=entry,designation=personnel_designation)
        issue = CompliancePersonnelIssue.objects.get(entry=entry,personnel=personnel,is_deleted=False)
        return issue
    except:
        return None


@register.simple_tag
def get_personnel_issues(entry):

    try:
        issue = CompliancePersonnelIssue.objects.filter(entry=entry, is_deleted=False).order_by('-id')
        return issues
    except:
        return None


#get contractors/p_managers 
@register.simple_tag
def get_contractors():
    p_managers = User.objects.filter(is_projectmanager=True, is_deleted=False)

    return p_managers


#get all acknowledged reports
@register.simple_tag
def get_all_acknowledged_reports():
    entries = ComplianceRecordEntry.objects.filter(is_published=True, is_deleted=False, is_active=True).order_by('-id') or None

    if not entries:
        return None
    else:
        return entries 


#get all rejected reports
@register.simple_tag
def get_all_rejected_reports():
    entries = ComplianceRecordEntry.objects.filter(is_rejected=True, is_deleted=False, is_active=True).order_by('-id') or None

    if not entries:
        return None
    else:
        return entries 

#get staff reviewers
@register.simple_tag
def get_all_staff(request):
    if request.user.is_admin or request.user.is_staff:
        staff = User.objects.filter(is_deleted = False, is_staff = True, is_reviewer = True)

        if not staff:
            return None
        else:
            return staff




#get all compliance records
@register.simple_tag
def get_all_noncompliance_records(request):
    reports = Inspection.objects.filter( is_deleted=False).order_by('-id') or None

    if not reports:
        return None
    else:
        return reports


#get all compliance records pending team leader review
@register.simple_tag
def get_pending_noncompliance_teamlead_records(request):
    reports = Inspection.objects.filter( is_deleted=False,status='PENDING_TEAM_LEADER_REVIEW').order_by('-id') or None

    if not reports:
        return None
    else:
        return reports


#get all compliance records pending manager review
@register.simple_tag
def get_pending_noncompliance_management_records(request):
    reports = Inspection.objects.filter( is_deleted=False,status='PENDING_MANAGER_REVIEW').order_by('-id') or None

    if not reports:
        return None
    else:
        return reports


#get all compliance records pending manager review
@register.simple_tag
def get_noncompliance_records(request,status='PUBLISHED'):
    reports = Inspection.objects.filter( is_deleted=False,status=status).order_by('-id') or None

    if not reports:
        return None
    else:
        return reports


@register.simple_tag
def get_default_objects(request):
    default_reports = ComplianceRecord.objects.filter(is_deleted=False)
    month_choices = settings.MONTH_CHOICES
    default_record_types = settings.COMPLIANCE_RECORD_TYPE
    default_module_types = settings.COMPLIANCE_MODULE_TYPE

    return {
            'default_reports':default_reports,
            'month_choices':month_choices,
            'default_record_types':default_record_types,
            'default_module_types':default_module_types
        }

    