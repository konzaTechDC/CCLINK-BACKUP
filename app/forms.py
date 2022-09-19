"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import *
from django.conf import settings
from django.contrib.auth import get_user_model
from app.models import *
from jsignature.forms import JSignatureField
from jsignature.widgets import JSignatureWidget

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))


class ComplianceRecordForm(forms.ModelForm):
    class Meta:  
        model = ComplianceRecord  
        fields = ('organization_name', 'notes', 'type')
        labels = {
                'organization_name':_('organization name'),
                'notes':_('Notes'),
                'type':_('Type'),
            }
        localized_fields = "__all__"
        widgets = {
            'notes': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'notes': {
                'max_length': _("This notes is too long."),
            },
        }


class ComplianceRecordEntryForm(forms.ModelForm):
    
    class Meta:  
        model = ComplianceRecordEntry  
        fields = ('month','year','summary','project_name', 'signature', 'review')
        labels = {
                'summary':_('Summary'),
                'review':_('Review'),
                'month':_('Month'),
                'year':_('Year'),
                'project_name':_('Project Name'),
                'signature':_('Signature'),
            }
        localized_fields = "__all__"
        widgets = {
            'summary': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
            'review': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
            'month':forms.Select(attrs={'class':"form-control col-md-7 "}),
            'year':forms.Select(attrs={'class':"form-control col-md-7 "}),
            'designation_name': forms.TextInput(attrs={'class':'form-control','placeholder':'Project Name'}),
            'signature':JSignatureWidget(jsignature_attrs={'color': '#CCC'})
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'summary': {
                'max_length': _("This notes is too long."),
            },
        }


class PersonnelDesignationForm(forms.ModelForm):
    class Meta:  
        model = PersonnelDesignation  
        fields = ('type','designation_name')
        labels = {
                'type':_('type'),
                'designation_name':_('designation_name'),
                
            }
        localized_fields = "__all__"
        widgets = {
           'designation_name': forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Site agent - Security', 'required':''}),
           'type': forms.Select(attrs={'class':'form-control','required':''}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'first_name': {
                'designation_name': _("This designation name is too long."),
            },
        }


class PersonnelForm(forms.ModelForm):
    class Meta:  
        model = Personnel  
        fields = ('first_name', 'other_name','email','tel_number','designation','signature')
        labels = {
                'first_name':_('first name'),
                'other_name':_('other name'),
                'email':_('email'),
                'tel_number':_('tel_number'),
                'designation':_('designation'),
                'signature':_('signature')
            }
        localized_fields = "__all__"
        widgets = {
            'summary': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'first_name': {
                'max_length': _("This first name is too long."),
            },
        }


class PersonnelDocumentForm(forms.ModelForm):
    class Meta:  
        model = PersonnelDocument  
        fields = ('type', 'attachment','description')
        labels = {
                'type':_('Type'),
                'attachment':_('attachment'),
               'description':_('description'),
            }
        localized_fields = "__all__"
        widgets = {
            'type': forms.Select(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'cols': 20, 'rows': 10,'class':'form-control'}),
           # 'attachment': forms.FileField(attrs={'class':'form-control'}),
        }
        help_texts = {
            'attachment': _('Upload  professional practicing licenses, work permits, and reports on new staff onboarded within the reporting period.'),
        }
        error_messages = {
            'description': {
                'max_length': _("This description is too long."),
            },
        }


class ComplianceModuleForm(forms.ModelForm):
    class Meta:  
        model = ComplianceModule  
        fields = ('name', 'type', 'notes')
        labels = {
                'type':_('Type'),
                'name':_('name'),
                'notes':_('notes'),
                
            }
        localized_fields = "__all__"
        widgets = {
            'notes': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'notes': {
                'max_length': _("This notes is too long."),
            },
        }


class ComplianceModuleReferenceForm(forms.ModelForm):
    class Meta:  
        model = ComplianceModuleReference  
        fields = ('reference', 'parameter', 'notes')
        labels = {
                'reference':_('Reference'),
                'parameter':_('parameter'),
                'notes':_('notes'),
                
            }
        localized_fields = "__all__"
        widgets = {
            'notes': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'notes': {
                'max_length': _("This notes is too long."),
            },
        }


class ComplianceReferenceRequirementForm(forms.Form):
     class Meta:  
        model = ComplianceReferenceRequirement  
        fields = ('requirement_name', 'notes')
        labels = {
                'requirement_name':_('requirement name'),
                'notes':_('notes'),
                
            }
        localized_fields = "__all__"
        widgets = {
            'notes': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'notes': {
                'max_length': _("This notes is too long."),
            },
        }


class ComplianceRequirementAttachmentDetailsForm(forms.Form):
    class Meta:  
        model = ComplianceRequirementAttachmentDetails
        fields = ('document_name', 'notes')
        labels = {
                'document_name':_('document name'),
                'notes':_('notes'),
                
            }
        localized_fields = "__all__"
        widgets = {
            'notes': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'notes': {
                'max_length': _("This notes is too long."),
            },
        }


class ComplianceRequirementAttachmentSubmissionForm(forms.Form):
    class Meta:  
        model = ComplianceRequirementAttachmentSubmission  
        fields = ('attachment')
        labels = {
                'attachment':_('attachment'),
                
            }
        localized_fields = "__all__"
        widgets = {
            'notes': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            'attachment': _('Upload documents.'),
        }
        error_messages = {
          #  'notes': {
            #    'max_length': _("This notes is too long."),
            #},
        }


class ComplianceRequirementMetricForm(forms.Form):
    class Meta:  
        model = ComplianceRequirementMetric
        fields = ('metric_type', 'notes')
        labels = {
                'metric_type':_('metric_type'),
                'notes':_('help notes'),
                
            }
        localized_fields = "__all__"
        widgets = {
            'notes': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'notes': {
                'max_length': _("This notes is too long."),
            },
        }


class ComplianceRequirementMetricSubmissionForm(forms.Form):
    class Meta:  
        model = ComplianceRequirementMetric
        fields = ( 'notes')
        labels = {
                'notes':_('notes'),
                
            }
        localized_fields = "__all__"
        widgets = {
            'notes': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'notes': {
                'max_length': _("This notes is too long."),
            },
        }


class ComplianceRequirementIssueForm(forms.Form):
    class Meta:  
        model = ComplianceRequirementIssue
        fields = ( 'notes')
        labels = {
                'notes':_('notes'),
                
            }
        localized_fields = "__all__"
        widgets = {
            'notes': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'notes': {
                'max_length': _("This notes is too long."),
            },
        }


class InspectionForm(forms.Form):
    class Meta:  
        model = Inspection
        fields = ( 'observation', 'action', 'module', 'reference','coordinates')
        labels = {
                'observation':_('Observation'),
                'action':_('Action'),
                'coordinates':_('Coordinates'),
                'module':_('Module'),
                'reference':_('Reference'),
                
            }
        localized_fields = "__all__"
        widgets = {
            'observation': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
            'action': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
            'coordinates': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'observation': {
                'max_length': _("This observation statement is too long."),
            },
            'action': {
                'max_length': _("This action statement is too long."),
            },
            'coordinates': {
                'max_length': _("This coordinates statement is too long."),
            },
        }



class InspectionPhotoEvidenceForm(forms.Form):
    class Meta:  
        model = InspectionPhotoEvidence
        fields = ( 'file', 'caption')
        labels = {
                'file':_('Photo evidence'),
                'caption':_('caption'),
                
            }
        localized_fields = "__all__"
        widgets = {
            #'observation': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
            'caption': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'file': {
               # 'max_length': _("This observation statement is too long."),
            },
            'caption': {
                'max_length': _("This caption statement is too long."),
            },
        }

class InspectionVideoEvidenceForm(forms.Form):
    class Meta:  
        model = InspectionVideoEvidence
        fields = ( 'file', 'caption')
        labels = {
                'file':_('Video evidence'),
                'caption':_('caption'),
                
            }
        localized_fields = "__all__"
        widgets = {
            #'observation': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
            'caption': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'file': {
               # 'max_length': _("This observation statement is too long."),
            },
            'caption': {
                'max_length': _("This caption statement is too long."),
            },
        }



class InspectionCommentsForm(forms.Form):
    class Meta:  
        model = InspectionComments
        fields = ( 'comment',)
        labels = {
                'comment':_('Comment'),
                
            }
        localized_fields = "__all__"
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'comment': {
               # 'max_length': _("This observation statement is too long."),
            },
            
        }