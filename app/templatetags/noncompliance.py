from django import template
from app.models import *

register = template.Library()

@register.simple_tag
def get_issue(entry, requirement):

    try:
        issue = ComplianceRequirementIssue.objects.get(entry=entry,requirement=requirement, is_deleted=False)
        return issue
    except:
        return None


#get non compliance issues fro an entry
@register.simple_tag
def get_issues(entry):

    try:
        issues = ComplianceRequirementIssue.objects.filter(entry=entry, is_deleted=False)
        return issues
    except:
        return None


@register.simple_tag
def get_requirement_issues(entry, requirement):

    try:
        issues = ComplianceRequirementIssue.objects.filter(entry=entry,requirement=requirement, is_deleted=False) or None
        return issues
    except:
        return None


@register.simple_tag
def get_personnel_issue(entry, personnel):

    try:
        issue = CompliancePersonnelIssue.objects.get(entry=entry,personnel=personnel, is_deleted=False)
        return issue
    except:
        return None


@register.simple_tag
def get_personnel_issues(entry):

    try:
        issues = CompliancePersonnelIssue.objects.filter(entry=entry, is_deleted=False)
        return issues
    except:
        return None


@register.simple_tag
def get_previous_personnel_issue(entry, personnel_designation):

    try:
        personnel = Personnel.objects.get(record_entry=entry,designation=personnel_designation, is_deleted=False)
        issue = CompliancePersonnelIssue.objects.get(entry=entry,personnel=personnel, is_deleted=False)
        return issue
    except:
        return None


@register.simple_tag
def get_pending_requirements(entry):
    metric_submissions =  ComplianceRequirementMetricSubmission.objects.filter(record_entry=entry,notes=None)
    if metric_submissions:
        return metric_submissions
    else:
        return None

