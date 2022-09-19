"""
Customizations for the Django administration interface.
"""

from django.contrib import admin
from app.models import *
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea


class ComplianceRecordAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('organization_name', 'notes', 'is_active' ,'type')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('organization_name', 'notes', 'is_active','type'),
            }),
        )
    list_display = ('organization_name', 'notes', 'is_active','type')

    search_fields = ['organization_name', 'notes']
admin.site.register(ComplianceRecord, ComplianceRecordAdmin)


class ContractorProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('company_name', 'project_manager', 'is_active' ,'is_deleted')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('company_name', 'project_manager', 'is_active','is_deleted'),
            }),
        )
    list_display = ('company_name', 'project_manager', 'is_active','is_deleted')

    search_fields = ['company_name', 'project_manager']
admin.site.register(ContractorProfile, ContractorProfileAdmin)


class ComplianceRecordEntryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('compliance_record','project_name', 'summary','signature', 'is_published', 'is_active' ,'month', 'year','review')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('compliance_record', 'project_name', 'summary', 'is_active','summary','signature', 'is_published','month', 'year', 'review'),
            }),
        )
    list_display = ('compliance_record', 'project_name', 'summary', 'is_active','month', 'year', 'review')

    search_fields = ['compliance_record', 'project_name', 'summary','month', 'year', 'review']
admin.site.register(ComplianceRecordEntry, ComplianceRecordEntryAdmin)


class PersonnelDesignationAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('record', 'type','designation_name')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('record', 'type','designation_name'),
            }),
        )
    list_display = ('record', 'type','designation_name')

    search_fields = [ 'type','designation_name']
admin.site.register(PersonnelDesignation, PersonnelDesignationAdmin)



class PersonnelAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('record_entry', 'first_name','other_name', 'email', 'tel_number' ,'signature')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('record_entry', 'first_name', 'other_name','email','signature', 'tel_number','designation'),
            }),
        )
    list_display = ('record_entry', 'first_name', 'other_name','email', 'tel_number', 'signature', 'designation')

    search_fields = ['first_name', 'other_name', 'email', 'tel_number', 'designation']
admin.site.register(Personnel, PersonnelAdmin)


class PersonnelDocumentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('personnel', 'description','type', 'attachment')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('personnel', 'description', 'type','attachment'),
            }),
        )
    list_display = ('personnel', 'description', 'type','attachment')

    search_fields = ['description' 'type', 'attachment']
admin.site.register(PersonnelDocument, PersonnelDocumentAdmin)

class ComplianceModuleAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('compliance_record', 'name','type', 'notes')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('compliance_record', 'name', 'type','notes'),
            }),
        )
    list_display = ('compliance_record', 'name', 'type','notes')

    search_fields = ['compliance_record', 'name', 'notes']
admin.site.register(ComplianceModule, ComplianceModuleAdmin)


class ComplianceModuleReferenceAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('module', 'reference','parameter', 'notes')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('module', 'reference', 'parameter','notes'),
            }),
        )
    list_display = ('module', 'reference', 'parameter','notes')

    search_fields = ['reference', 'name', 'parameter', 'notes']
admin.site.register(ComplianceModuleReference, ComplianceModuleReferenceAdmin)


class ComplianceReferenceRequirementAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('reference', 'requirement_name','notes')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('requirement_name', 'reference','notes'),
            }),
        )
    list_display = ('requirement_name', 'reference', 'notes')

    search_fields = ['reference', 'requirement_name',  'notes']
admin.site.register(ComplianceReferenceRequirement, ComplianceReferenceRequirementAdmin)


class ComplianceRequirementAttachmentDetailsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('requirement', 'document_name','notes')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('document_name', 'requirement','notes'),
            }),
        )
    list_display = ('document_name', 'requirement', 'notes')

    search_fields = ['document_name', 'requirement',  'notes']
admin.site.register(ComplianceRequirementAttachmentDetails, ComplianceRequirementAttachmentDetailsAdmin)


class ComplianceRequirementAttachmentSubmissionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('requirement_detail', 'attachment')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('requirement_detail', 'attachment'),
            }),
        )
    list_display = ('requirement_detail',  'attachment')

    search_fields = ['requirement_detail', 'attachment']
admin.site.register(ComplianceRequirementAttachmentSubmission, ComplianceRequirementAttachmentSubmissionAdmin)


class ComplianceRequirementMetricAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('requirement', 'metric_type', 'notes')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('requirement','metric_type', 'notes'),
            }),
        )
    list_display = ('requirement',  'metric_type', 'notes')

    search_fields = ['requirement', 'metric_type', 'notes']
admin.site.register(ComplianceRequirementMetric, ComplianceRequirementMetricAdmin)


class ComplianceRequirementMetricSubmissionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('metric', 'record_entry', 'notes')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('metric', 'record_entry', 'notes'),
            }),
        )
    list_display = ('metric',  'record_entry', 'notes')

    search_fields = [ 'notes']
admin.site.register(ComplianceRequirementMetricSubmission, ComplianceRequirementMetricSubmissionAdmin)


class ComplianceRequirementIssueAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('requirement', 'entry', 'is_resolved', 'notes')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('requirement', 'entry', 'is_resolved', 'notes'),
            }),
        )
    list_display = ('requirement',  'entry', 'is_resolved', 'notes')

    search_fields = [ 'notes']
admin.site.register(ComplianceRequirementIssue, ComplianceRequirementIssueAdmin)


class CompliancePersonnelIssueAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('personnel', 'entry', 'is_resolved', 'notes')}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('personnel', 'entry', 'is_resolved', 'notes'),
            }),
        )
    list_display = ('personnel',  'entry', 'is_resolved', 'notes')

    search_fields = [ 'notes']
admin.site.register(CompliancePersonnelIssue, CompliancePersonnelIssueAdmin)
