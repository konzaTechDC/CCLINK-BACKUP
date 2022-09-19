"""
Definition of models.
"""

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from jsignature.fields import JSignatureField
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import datetime
from user_auth.models import *
import uuid

from django import template

register = template.Library()

# Compliance record holds all the instaces of static data form labels e.t.c. Keep it at one record only to be safe.
class ComplianceRecord(models.Model):
    #name of organization that does the compliance check. i.e. KOTDA
    organization_name = models.CharField(
                 _('organization name'),
                max_length=200,
                null=False,
                blank=False,
                error_messages ={ 
                    "max_length":"The organization name is too long. Use a maximum of 200 characters."
                    } 
                )

    
    notes = models.TextField(
                    _('notes'),
                max_length=2000,
                null=True,
                blank=True,
                error_messages ={ 
                    "max_length":"The notes is too long. Use a maximum of 2000 characters."
                    } 
                )
    #type of compliance record type i.e construction e.t.c
    type = models.CharField(
                _('type'),
            max_length=200,
            null=False,
            blank=False,
            choices=settings.COMPLIANCE_RECORD_TYPE,
            error_messages ={ 
                "max_length":"The type is too long. Use a maximum of 200 characters."
                } 
            )
    #no functionalilty has been designed for this. safe to leave at false.
    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    #leave it at true on production to be safe
    is_active = models.BooleanField(default=False)
    #if true, contractors can submit. if false, contractors can not submit
    submission_enabled = models.BooleanField(default=False);
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organization_name + "|" + self.type 

    #get the areas of compliance, e.g. QA, health etc...
    def get_compliance_modules(self):
        modules = ComplianceModule.objects.filter(compliance_record=self)
        return modules



#contractor profile

# Only contractor accounts have a profile
class ContractorProfile(models.Model):
    #name of contractor company
    company_name = models.CharField(
                 _('company name'),
                max_length=200,
                null=False,
                blank=False,
                error_messages ={ 
                    "max_length":"The company name is too long. Use a maximum of 200 characters."
                    } 
                )
    #user account responsible for compliance reports
    project_manager = models.OneToOneField(User, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    is_active = models.BooleanField(default=False)
    #contractor can be blocked by PPDC from submitting reports
    is_blocked = models.BooleanField(default=False)
    #reason for blocking
    block_reason = models.TextField(
                    _('block reason'),
                max_length=2000,
                null=True,
                blank=True,
                error_messages ={ 
                    "max_length":"The block_reason is too long. Use a maximum of 2000 characters."
                    } 
                )
    #user that blocked contractor. Usually its the Chief manager
    blocked_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="blocked_by")
    blocked_at = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.company_name) 
    #get reports submitted by this profile
    def get_compliance_submissions(self):
        submissions = ComplianceRecordEntry.objects.filter(created_by=self.project_manager, is_active=True, is_deleted=False)
        return submissions

    def get_compliance_record(self):
        submissions = ComplianceRecordEntry.objects.filter(created_by=self.project_manager, is_active=True, is_deleted=False)

        return submissions(0).compliance_record


    def get_noncompliance_notifications(self):
        notifications =  Inspection.objects.filter(status='PUBLISHED',is_deleted=False,contractor=self) or None
        return notifications
    

    
    #Compliance record entry: this is the account bein filled
class ComplianceRecordEntry(models.Model):
    compliance_record = models.ForeignKey(ComplianceRecord, on_delete=models.CASCADE)
    report_uid=models.UUIDField(editable=False,max_length=10, blank=True, null=True, unique=True, primary_key=False, default=uuid.uuid4)
    project_name = models.CharField(
                _('project_name'),
            max_length=200,
            null=False,
            blank=False,
            error_messages ={ 
                "max_length":"The name is too long. Use a maximum of 200 characters."
                } 
            )
    
    summary = models.TextField(
                _('summary'),
            max_length=5000,
            null=True,
            blank=True,
            error_messages ={ 
                "max_length":"The summary is too long. Use a maximum of 5000 characters."
                } 
            )

    review = models.TextField(
                _('Review'),
            max_length=5000,
            null=True,
            blank=True,
            error_messages ={ 
                "max_length":"The review is too long. Use a maximum of 5000 characters."
                } 
            )



    month = models.CharField(
                _('month'),
            max_length=20,
            null=False,
            blank=False,
            default=datetime.now().month,
            choices=settings.MONTH_CHOICES,
            error_messages ={ 
                "max_length":"The month is too long. Use a maximum of 20 characters."
                } 
            )

    status = models.CharField(
                _('status'),
            max_length=20,
            null=False,
            blank=False,
            choices=settings.PUBLISH_STATUS,
            default='draft',
            error_messages ={ 
                "max_length":"The month is too long. Use a maximum of 20 characters."
                } 
            )

    YEAR_CHOICES = []
    for r in range(1980, (datetime.now().year+1)):
        YEAR_CHOICES.append((r,r))

    year = models.IntegerField(_('year'), choices=YEAR_CHOICES, 
           default=datetime.now().year)
    signature = JSignatureField(null=True,blank=True)
    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    is_rejected = models.BooleanField(default=False)#this remains false until PPDC rejects report
    is_published = models.BooleanField(default=False)#thisremains false until ppdc acknowledges report
    is_published_with_comments = models.BooleanField(default=False)#thisremains false until ppdc acknowledges report with comments
    is_active = models.BooleanField(default=False)#this remains false until contractor submits the report
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,related_name="last_updated_by")
    created_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="created_by")#the project manager account
    submitted_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="submitted_by")
    submitted_at = models.DateTimeField(null=True,blank=True)
    evaluated_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="evaluated_by")
    deleted_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="deleted_by")

    def __str__(self):
        return str(self.month) + str(self.year)

    def get_metric_submissions(self):
        submissions = ComplianceRequirementMetricSubmission.objects.filter(record_entry=self)
        return submissions

    def get_personnel(self):
        personnel = Personnel.objects.filter(record_entry=self, is_deleted=False)
        return personnel

    def get_month(self):

        if self.month == '1':
            month = 'January'
        elif self.month == '2':
            month = 'February'
        elif self.month == '3':
            month = 'March'
        elif self.month == '4':
            month = 'April'
        elif self.month == '5':
            month = 'May'
        elif self.month == '6':
            month = 'June'
        elif self.month == '7':
            month = 'July'
        elif self.month == '8':
            month = 'August'
        elif self.month == '9':
            month = 'September'
        elif self.month == '10':
            month = 'October'
        elif self.month == '11':
            month = 'November'
        elif self.month == '12':
            month = 'December'
        else:
            month = 'Undated'

        return month


#report inheritance
class EntryInheritance(models.Model):
    child = models.ForeignKey(ComplianceRecordEntry, null=True,blank=True, on_delete=models.CASCADE,related_name="child")
    parent = models.ForeignKey(ComplianceRecordEntry, null=True,blank=True, on_delete=models.CASCADE,related_name="parent")
    created_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="user")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("parent", "child")


    ########################################################################
    #personnel designation
    ########################################################################

class PersonnelDesignation(models.Model):
    record = models.ForeignKey(ComplianceRecord, on_delete=models.CASCADE)
    designation_name = models.CharField(
                _('designation name'),
                max_length=200,
                null=True,
                blank=True,
                #choices=settings.DESIGNATION_TYPES,
                error_messages ={ 
                    "max_length":"The designation name is too long. Use a maximum of 200 characters."
                    }
        )
    type = models.CharField(
            _('type'),
            max_length=200,
            null=True,
            blank=True,
            choices=settings.PERSONNEL_TYPES,
            error_messages ={ 
                "max_length":"The type is too long. Use a maximum of 200 characters."
                } 
            )
    is_extra = models.BooleanField(_('is extra'),default=False,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True, related_name="personneldeg_last_updated_by")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,related_name="personneldeg_created_by")

    def __str__(self):
        return str(self.designation_name)


    ########################################################################
    #Personnel
    ########################################################################
class Personnel(models.Model):
    record_entry = models.ForeignKey(ComplianceRecordEntry, on_delete=models.CASCADE)
    designation = models.ForeignKey(PersonnelDesignation, on_delete=models.CASCADE)
    first_name = models.CharField(
                 _('first name'),
                max_length=200,
                null=True,
                blank=True,
                error_messages ={ 
                    "max_length":"The first name is too long. Use a maximum of 200 characters."
                    } 
        )
    other_name = models.CharField(
                _('other name'),
                max_length=200,
                null=True,
                blank=True,
                error_messages ={ 
                    "max_length":"The other name is too long. Use a maximum of 200 characters."
                    }
        )
    email = models.EmailField(null=True,blank=True,)
    tel_number = PhoneNumberField(null=True,blank=True,)
    signature = JSignatureField(null=True,blank=True,)
    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True, related_name="personnel_last_updated_by")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,related_name="personnel_created_by")
    def __str__(self):
        return str(self.first_name)

    def get_attachments(self):
        attachments = PersonnelDocument.objects.filter(personnel=self, is_deleted=False)

        return attachments


    ########################################################################
    #Personnel Documents
    ########################################################################
class PersonnelDocument(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)


    description = models.TextField(
                 _('description'),
                max_length=2000,
                null=True,
                blank=True,
                error_messages ={ 
                    "max_length":"The description is too long. Use a maximum of 2000 characters."
                    } 
                )

    type = models.CharField(
                 _('type'),
                max_length=200,
                null=True,
                blank=True,
                choices=settings.PERSONNEL_DOCUMENT_TYPE,
                error_messages ={ 
                    "max_length":"The hint is too long. Use a maximum of 200 characters."
                    } 
                )
    attachment = models.FileField(
        upload_to='personnel_attachment/',
        null=True,
        blank=True,
        )

    is_deleted = models.BooleanField(null=False,blank=False,default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,related_name="last_person_uploaded_by")
    created_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="uploaded_by")

    def __str__(self):
        return str(self.attachment)



    ########################################################################
    #compliance modules
    ########################################################################
class ComplianceModule(models.Model):
    compliance_record = models.ForeignKey(ComplianceRecord, on_delete=models.CASCADE)
    name = models.CharField(
                 _('name'),
                max_length=200,
                null=False,
                blank=False,
                error_messages ={ 
                    "max_length":"The module name is too long. Use a maximum of 200 characters."
                    } 
                )

    type = models.CharField(
                _('type'),
            max_length=200,
            null=False,
            blank=False,
            choices=settings.COMPLIANCE_MODULE_TYPE,
            error_messages ={ 
                "max_length":"The type is too long. Use a maximum of 200 characters."
                } 
            )

    notes = models.TextField(
                 _('notes'),
                max_length=2000,
                null=False,
                blank=False,
                error_messages ={ 
                    "max_length":"The notes is too long. Use a maximum of 2000 characters."
                    } 
                )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    def get_compliance_references(self):
        references = ComplianceModuleReference.objects.filter(module=self)
        return references

       ########################################################################
    #References
    ########################################################################
class ComplianceModuleReference(models.Model):
    module = models.ForeignKey(ComplianceModule, on_delete=models.CASCADE)
    reference = models.CharField(
                 _('reference'),
                max_length=200,
                null=False,
                blank=False,
                error_messages ={ 
                    "max_length":"The reference name is too long. Use a maximum of 200 characters."
                    } 
                )

    parameter = models.CharField(
                _('parameter'),
            max_length=200,
            null=False,
            blank=False,
            error_messages ={ 
                "max_length":"The parameter name is too long. Use a maximum of 200 characters."
                } 
            )


    notes = models.TextField(
                 _('notes'),
                max_length=2000,
                null=False,
                blank=False,
                error_messages ={ 
                    "max_length":"The note is too long. Use a maximum of 2000 characters."
                    } 
                )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.reference)

    def get_reference_requirements(self):
        requirements = ComplianceReferenceRequirement.objects.filter(reference=self)
        return requirements


       ########################################################################
    #Requirements
    ########################################################################
class ComplianceReferenceRequirement(models.Model):
    reference = models.ForeignKey(ComplianceModuleReference, on_delete=models.CASCADE)
    requirement_name = models.CharField(
            _('requirement name'),
        max_length=200,
        null=False,
        blank=False,
        error_messages ={ 
            "max_length":"The requirement name is too long. Use a maximum of 200 characters."
            } 
        )

    notes = models.TextField(
                _('notes'),
            max_length=2000,
            null=False,
            blank=False,
            error_messages ={ 
                "max_length":"The note is too long. Use a maximum of 2000 characters."
                } 
            )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.requirement_name)

    def get_metrics(self):
        metrics = ComplianceRequirementMetric.objects.filter(requirement=self)
        return metrics

  

    def get_attachment_details(self):
        attachments = ComplianceRequirementAttachmentDetails.objects.filter(requirement=self)
        return attachments

    def get_attachment_detail(self):
        attachment = ComplianceRequirementAttachmentDetails.objects.get(requirement=self)
        return attachment


       ########################################################################
    #Requirement attachment form details
    ########################################################################
class ComplianceRequirementAttachmentDetails(models.Model):
    requirement = models.ForeignKey(ComplianceReferenceRequirement, on_delete=models.CASCADE)

    document_name = models.CharField(
            _('document name'),
        max_length=200,
        null=False,
        blank=False,
        error_messages ={ 
            "max_length":"The document name is too long. Use a maximum of 200 characters."
            } 
        )

    notes = models.TextField(
            _('notes'),
        max_length=2000,
        null=False,
        blank=False,
        error_messages ={ 
            "max_length":"The note is too long. Use a maximum of 2000 characters."
            } 
        )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.document_name)

    def get_submissions(self):
        submissions = ComplianceRequirementAttachmentSubmission.objects.filter(requirement_detail=self)
        return submissions

       ########################################################################
    #Compliance requirement attachment submissions
    ########################################################################
class ComplianceRequirementAttachmentSubmission(models.Model):
    requirement_detail = models.ForeignKey(ComplianceRequirementAttachmentDetails, on_delete=models.CASCADE)
    record_entry = models.ForeignKey(ComplianceRecordEntry, on_delete=models.CASCADE)

    attachment = models.FileField(
        upload_to='compliance_attachment/',
        null=True,
        blank=True,
        )

    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,related_name="attachment_uploaded_by")
    uploaded_at = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,related_name="attachment_last_updated_by")

    def __str__(self):
        return str(self.attachment.name)

    ########################################################################
    #Compliance requirement metrics eg RFI 
    ########################################################################
class ComplianceRequirementMetric(models.Model):
    requirement = models.ForeignKey(ComplianceReferenceRequirement, on_delete=models.CASCADE)
    metric_type = models.CharField(
                _('type'),
                max_length=200,
                null=False,
                blank=False,
                choices=settings.COMPLIANCE_REQUIREMENT_METRIC_TYPE,
                error_messages ={ 
                "max_length":"The type is too long. Use a maximum of 200 characters."
                } 
            )

    input_type = models.CharField(
                _('type'),
                max_length=200,
                null=False,
                blank=False,
                default='text',
                choices=settings.COMPLIANCE_METRIC_INPUT_TYPE,
                error_messages ={ 
                "max_length":"The type is too long. Use a maximum of 200 characters."
                } 
            )

    notes = models.TextField(
            _('notes'),
            max_length=2000,
            null=False,
            blank=False,
            error_messages ={ 
            "max_length":"The note is too long. Use a maximum of 2000 characters."
            } 
        )
    is_required = models.BooleanField(_('is_required'), default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.metric_type)



    def get_submissions(self):
        try:
            submissions = ComplianceRequirementMetricSubmission.objects.filter(metric=self)
            return submissions
        except ComplianceRequirementMetricSubmission.DoesNotExist:
            return None
        

    ########################################################################
    #Compliance requirement metrics submitted data eg RFI 
    ########################################################################
class ComplianceRequirementMetricSubmission(models.Model):
    metric = models.ForeignKey(ComplianceRequirementMetric, on_delete=models.CASCADE)
    record_entry = models.ForeignKey(ComplianceRecordEntry, on_delete=models.CASCADE)

    notes = models.TextField(
            _('notes'),
            max_length=20000,
            null=True,
            blank=True,
            error_messages ={ 
            "max_length":"The note is too long. Use a maximum of 2000 characters."
            } 
        )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True, related_name="metric_last_updated_by")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,related_name="metric_created_by")

    def __str__(self):
        return str(self.notes)


    ########################################################################
#non-Compliance requirement reviews 
########################################################################
class ComplianceRequirementIssue(models.Model):
    
    entry = models.ForeignKey(ComplianceRecordEntry, on_delete=models.CASCADE)
    requirement = models.ForeignKey(ComplianceReferenceRequirement, on_delete=models.CASCADE)

    notes = models.TextField(
            _('notes'),
            max_length=20000,
            null=True,
            blank=True,
            error_messages ={ 
            "max_length":"The note is too long. Use a maximum of 2000 characters."
            } 
        )
    #choices can be 
    is_resolved = models.BooleanField(
                _('is resolved'),
            max_length=200,
            null=False,
            default=False,
            error_messages ={ 
                #"max_length":"The status is too long. Use a maximum of 200 characters."
                } 
            )
    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)

    ########################################################################
# personnel non-Compliance requirement reviews 
########################################################################
class CompliancePersonnelIssue(models.Model):
    
    entry = models.ForeignKey(ComplianceRecordEntry, on_delete=models.CASCADE)
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)

    notes = models.TextField(
            _('notes'),
            max_length=20000,
            null=True,
            blank=True,
            error_messages ={ 
            "max_length":"The note is too long. Use a maximum of 2000 characters."
            } 
        )
    #choices can be 
    is_resolved = models.BooleanField(
                _('is resolved'),
            max_length=200,
            null=False,
            default=False,
            error_messages ={ 
                #"max_length":"The status is too long. Use a maximum of 200 characters."
                } 
            )
    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)

    
    #########################################################################
#
#
#
# non-Compliance inspections
########################################################################
class Inspection(models.Model):
    inspection_uid = models.CharField(
            _('inspection_uid'),
        max_length=200,
        null=True,
        blank=True,
        error_messages = { 
            "max_length":"The inspection uid is too long. Use a maximum of 200 characters."
            } 
        )

    contractor = models.ForeignKey(ContractorProfile, null=False,blank=False, on_delete=models.CASCADE)
    module = models.ForeignKey(ComplianceModule,null=True,blank=True,on_delete=models.CASCADE)
    reference = models.ForeignKey(ComplianceModuleReference,null=True,blank=True,on_delete=models.CASCADE)
    observation = models.TextField(
            _('observation'),
            max_length=20000,
            null=False,
            blank=True,
            default='[UNSPECIFIED]',
            error_messages ={ 
            "max_length":"Your observation is too long. Use a maximum of 20000 characters."
            } 
        )
    
    
    action = models.TextField(
            _('action'),
            max_length=20000,
            null=False,
            blank=True,
            default='[UNSPECIFIED]',
            error_messages ={ 
            "max_length":"Your action statement is too long. Use a maximum of 20000 characters."
            } 
        )

    coordinates = models.TextField(
            _('coordinates'),
            max_length=20000,
            null=True,
            blank=True,
            default='[UNSPECIFIED]',
            error_messages ={ 
            "max_length":"Your action statement is too long. Use a maximum of 20000 characters."
            } 
        )

    status = models.CharField(
                _('comment_type'),
                max_length=200,
                null=False,
                blank=False,
                default='DRAFT',
                choices=settings.COMPLIANCE_INSPECTION_STATUS,
                error_messages ={ 
                "max_length":"The comment type  is too long. Use a maximum of 200 characters."
                } 
            )

    is_resolved = models.BooleanField(
                _('is resolved'),
            max_length=200,
            null=False,
            default=False,
            error_messages ={ 
                #"max_length":"The status is too long. Use a maximum of 200 characters."
                } 
            )
    is_published = models.BooleanField(null=False,blank=False,default=False)
    published_at = models.DateTimeField(null=True,blank=True)
    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    deleted_at = models.DateTimeField(null=True,blank=True)
    is_rejected = models.BooleanField(null=False,blank=False,default=False)
    rejected_at = models.DateTimeField(null=True,blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,related_name="review_last_updated_by")
    created_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="review_created_by")
    submitted_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="review_submitted_by")
    submitted_at = models.DateTimeField(null=True,blank=True)
    assigned_team_lead = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="assigned_team_lead")#not used at the momment but might come in handy
    published_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="published_by")
    evaluated_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="review_evaluated_by")
    evaluated_at = models.DateTimeField(null=True,blank=True)
    rejected_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="review_rejected_by")
    deleted_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="review_deleted_by")

    def __str__(self):
        return str(self.month) + str(self.year)


    def get_photos(self):
        photos = InspectionPhotoEvidence.objects.filter(inspection=self, is_deleted=False)

        return photos


    def get_videos(self):
        videos = InspectionVideoEvidence.objects.filter(inspection=self, is_deleted=False)

        return videos

    def get_documents(self):
        documents = InspectionDocumentEvidence.objects.filter(inspection=self, is_deleted=False)

        return documents

    def get_contractor_evidence(self):
        evidence = InspectionContractorEvidence.objects.filter(inspection=self, is_deleted=False)

        return evidence

    def get_all_comments(self):
        comments = InspectionComments.objects.filter(inspection=self,is_deleted=False)

        return comments

    def get_reviewer_comments(self):
        comments = InspectionComments.objects.filter(inspection=self, is_reviewer_comment=True, is_deleted=False)

        return comments

    def get_teamleader_comments(self):
        comments = InspectionComments.objects.filter(inspection=self, is_teamleader_comment=True, is_deleted=False)

        return comments

    def get_manager_comments(self):
        comments = InspectionComments.objects.filter(inspection=self, is_manager_comment=True, is_deleted=False)

        return comments

    def get_contractor_comments(self):
        comments = InspectionComments.objects.filter(inspection=self, is_contractor_comment=True, is_deleted=False)

        return comments



########################################################################
# non-Compliance inspection document evidence
########################################################################
class InspectionDocumentEvidence(models.Model):
    inspection = models.ForeignKey(Inspection, null=False,blank=False, on_delete=models.CASCADE)
    file = models.FileField(upload_to='inspectionDocument/',null=False,blank=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE,null=False,blank=False)
    uploaded_at = models.DateTimeField(null=True,blank=True)
    caption = models.CharField(
                _('caption'),
                max_length=2000,
                null=True,
                blank=True,
                
                error_messages ={ 
                "max_length":"The caption is too long. Use a maximum of 2000 characters."
                } 
            )
    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file

    
    ########################################################################
# non-Compliance inspection photo evidence
########################################################################
class InspectionPhotoEvidence(models.Model):
    inspection = models.ForeignKey(Inspection, null=False,blank=False, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='inspectionImages/',null=False,blank=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE,null=False,blank=False)
    uploaded_at = models.DateTimeField(null=True,blank=True)
    caption = models.CharField(
                _('caption'),
                max_length=2000,
                null=True,
                blank=True,
                
                error_messages ={ 
                "max_length":"The caption is too long. Use a maximum of 2000 characters."
                } 
            )
    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file


    ########################################################################
# non-Compliance inspection video evidence
########################################################################
class InspectionVideoEvidence(models.Model):
    inspection = models.ForeignKey(Inspection, null=False,blank=False, on_delete=models.CASCADE)
    file = models.FileField(upload_to='inspectionVideo/', verbose_name="video url",null=False,blank=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE,null=False,blank=False)
    uploaded_at = models.DateTimeField(null=True,blank=True)
    caption = models.CharField(
                _('caption'),
                max_length=2000,
                null=True,
                blank=True,
                
                error_messages ={ 
                "max_length":"The caption is too long. Use a maximum of 2000 characters."
                } 
            )
    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file




########################################################################
# non-Compliance inspection document evidence from contractor
########################################################################
class InspectionContractorEvidence(models.Model):
    inspection = models.ForeignKey(Inspection, null=False,blank=False, on_delete=models.CASCADE)
    file = models.FileField(upload_to='inspectionContractorEvidence/',null=False,blank=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE,null=False,blank=False)
    uploaded_at = models.DateTimeField(null=True,blank=True)
    caption = models.CharField(
                _('caption'),
                max_length=2000,
                null=True,
                blank=True,
                
                error_messages ={ 
                "max_length":"The caption is too long. Use a maximum of 2000 characters."
                } 
            )
    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file

    
########################################################################
# non-Compliance inspection comments
########################################################################
class InspectionComments(models.Model):
    inspection = models.ForeignKey(Inspection, null=False,blank=False, on_delete=models.CASCADE)
    comment = models.TextField(
            _('comment'),
            max_length=20000,
            null=False,
            blank=False,
            error_messages ={ 
            "max_length":"Your observation is too long. Use a maximum of 20000 characters."
            } 
        )
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE,null=False,blank=False)
    comment_type = models.CharField(
                _('comment_type'),
                max_length=200,
                null=False,
                blank=False,
                default='MEMBER',
                choices=settings.COMPLIANCE_INSPECTION_COMMENT_TYPE,
                error_messages ={ 
                "max_length":"The comment type  is too long. Use a maximum of 200 characters."
                } 
            )

    is_reviewer_comment = models.BooleanField(null=False,blank=False,default=False)
    is_teamleader_comment = models.BooleanField(null=False,blank=False,default=False)
    is_manager_comment = models.BooleanField(null=False,blank=False,default=False)
    is_contractor_comment = models.BooleanField(null=False,blank=False,default=False)
    is_deleted = models.BooleanField(null=False,blank=False,default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)