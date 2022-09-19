"""
Definition of views.
"""
from __future__ import unicode_literals
import json
import os
import codecs
from os import path
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse, JsonResponse
from django.views import View
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import ListView, DetailView
from app.models import *
from django.utils.text import slugify
from django.http import QueryDict
from django.forms import formset_factory
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
#from dal import autocomplete
from app.compliance_context_preprocessors import *
from app.forms import *
from django.contrib.auth.decorators import *

from ComplianceReporting.tasks import send_email_task
from app.utils import render_to_pdf
import csv
from django.template import Template, Context
import random
from app.fiscal_date import GetFiscalYear

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
            'get_default_objects':get_default_objects(request),
        }
    )



def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
            'get_default_objects':get_default_objects(request)
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
            'get_default_objects':get_default_objects(request)
        }
    )

#returns GPS info
def get_exif(filename):
    exif = Image.open(filename)._getexif()

    if exif is not None:
        for key, value in exif.items():
            name = TAGS.get(key, key)
            exif[name] = exif.pop(key)

        if 'GPSInfo' in exif:
            for key in exif['GPSInfo'].keys():
                name = GPSTAGS.get(key,key)
                exif['GPSInfo'][name] = exif['GPSInfo'].pop(key)

    return exif


#upload class
class BasicUploadView(View):
    def get(self, request):
        photos_list = InspectionPhotoEvidence.objects.all()
        return render(self.request, 'compliance/inspection/create_inspection.html', {'photos': photos_list})

    def post(self, request):
        #use try to switch between contractor and staff uploads
        try:
            #check if its an inspection report
            ##
            #get form
            form = InspectionPhotoEvidenceForm(self.request.POST, self.request.FILES)
            #get inspection record from DB| use inspection_id from form.GET
            inspection = Inspection.objects.get(id=self.request.POST.get("inspection_id"))
            
            #check if its a photo upload
            if self.request.FILES.get("document"):
                #create new photo evidence record
                doc_evidence = InspectionDocumentEvidence()
                doc_evidence.file = self.request.FILES.get("document")
                doc_evidence.inspection = inspection;
                doc_evidence.uploaded_by = request.user
                doc_evidence.updated_at = datetime.now()
                doc_evidence.save()

                #return data if save is successful
                data = {'is_valid': True, 'name': doc_evidence.file.name, 'url': doc_evidence.file.url }
                return JsonResponse(data)

            #check if its a photo upload
            if self.request.FILES.get("contractor_evidence"):
                #create new photo evidence record
                contractor_evidence = InspectionContractorEvidence()
                contractor_evidence.file = self.request.FILES.get("contractor_evidence")
                contractor_evidence.inspection = inspection;
                contractor_evidence.uploaded_by = request.user
                contractor_evidence.updated_at = datetime.now()
                contractor_evidence.save()

                #return data if save is successful
                data = {'is_valid': True, 'name': contractor_evidence.file.name, 'url': contractor_evidence.file.url }
                return JsonResponse(data)

            #check if its a photo upload
            if self.request.FILES.get("photo"):
                #create new photo evidence record
                pic_evidence = InspectionPhotoEvidence()
                pic_evidence.file = self.request.FILES.get("photo")
                pic_evidence.inspection = inspection;
                pic_evidence.uploaded_by = request.user
                pic_evidence.updated_at = datetime.now()
                pic_evidence.save()

                #return data if save is successful
                data = {'is_valid': True, 'name': pic_evidence.file.name, 'url': pic_evidence.file.url }
                return JsonResponse(data)
            
            #check if its a video upload
            if self.request.FILES.get("video"):
                #create new video evidence record
                video_evidence = InspectionVideoEvidence()
                video_evidence.file = self.request.FILES.get("video")
                video_evidence.inspection = inspection;
                video_evidence.uploaded_by = request.user
                video_evidence.updated_at = datetime.now()
                video_evidence.save()

                #return data if save is successful
                data = {'is_valid': True, 'name': video_evidence.file.name, 'url': video_evidence.file.url}
                return JsonResponse(data)
        
            else:
                #return false if save failed
                data = {'is_valid': False}
                return JsonResponse(data)

        #if try process failed then it must be a contractor attachment
        except:
            #check if it has an attachment from contractor
            if self.request.FILES.get("attachment"):
                #create new attachment record
                attachment = ComplianceRequirementAttachmentSubmission()
                attachment.attachment = self.request.FILES.get("attachment")
                attachment.requirement_detail =ComplianceRequirementAttachmentDetails.objects.get(id=self.request.POST.get("attachment_detail_id"));
                attachment.record_entry =ComplianceRecordEntry.objects.get(id=self.request.POST.get("entry_id"));
                attachment.uploaded_by = request.user
                attachment.updated_at = datetime.now()
                attachment.last_updated_by = request.user
                attachment.save()

                #return data if save is successful
                data = {'is_valid': True, 'name': attachment.attachment.name, 'url': attachment.attachment.url}
                return JsonResponse(data)
        
            else:
                data = {'is_valid': False}
                return JsonResponse(data)
            pass
########################################################################################################################################

  #check if contractor has already subitted a report    
@login_required
def check_if_contractor_has_submitted(request,record):
    try:
        #check if its the correct date
        #check if contractor has already subitted a report
        if datetime.now().month-1 == 0:
            check_entry = ComplianceRecordEntry.objects.get(compliance_record=record, month=12, year=datetime.now().year-1, submitted_by = request.user, is_deleted=False, is_active=True)
        else:
            check_entry = ComplianceRecordEntry.objects.get(compliance_record=record, month=datetime.now().month-1, year=datetime.now().year, submitted_by = request.user, is_deleted=False, is_active=True)

        if check_entry is not None:
            #if an entry exists, return true
            return True
                      

    except ComplianceRecordEntry.DoesNotExist:
        #entry does not exist, return false
        return False
 ####################################################################################################################################################       


#main dashboard redirect function i.e. use this link for both contractors and staff dashboards
@login_required
def dashboard_view(request):
    records = ComplianceRecord.objects.filter(is_active=True)
    #if user is PM redirect to main dashboard
    if request.user.is_contractor or request.user.is_projectmanager:
        
        entry_form = ComplianceRecordEntryForm()
        #check if its submission period 
        if check_if_contractor_has_submitted(request,records[0]) == False:
            #set reminder message
            messages.add_message(request, messages.WARNING, 'You have not submitted your monthly report. Please submit your report before deadline.')
        if records is not None:
            return render(
                request,
                'compliance/dashboard.html',
                {
                    'title':'Compliance dashboard',
                    'message':'Manage your reports',
                    'year':datetime.now().year,
                    'tab':'draft',#default tab
                    'records':records,#compliance records
                    'entry_form':entry_form,#submission form
                    'get_default_objects':get_default_objects(request)#just include this to be safe
                }
    
            )
    #if user is staff redirect to staff dashboard
    elif request.user.is_staff:
        if records is not None:
            return redirect('staff_dashboard', request.user.id )

    #default redirect
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#####################################################################################################


#redirect function to switch dashboard tabs
@login_required
def dashboard_tab_view(request,tab):
    records = ComplianceRecord.objects.filter(is_active=True)
    entry_form = ComplianceRecordEntryForm()
    #if user is PM redirect to main dashboard
    if request.user.is_contractor or request.user.is_projectmanager:
        if records is not None:
            return render(
                request,
                'compliance/dashboard.html',
                {
                    'title':'Compliance dashboard- '+tab,
                    'message':'Manage your reports',
                    'year':datetime.now().year,
                    'tab':tab,
                    'records':records,
                    'entry_form':entry_form,
                    'get_default_objects':get_default_objects(request)
                }
    
            )
    #if user is staff redirect to staff dashboard
    elif request.user.is_staff or request.user.is_admin:
        if records is not None:
            return redirect('staff_dashboard', request.user.id )
    

    #default redirect
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#update contractor user and profile data: method only used by contractor updating own data
@login_required
def update_contractor_details(request):
    if request.method == 'POST':
        user = request.user
        #update db i.e. user and contractor_profile info
        if request.POST.get('username'):
            user.username = request.POST.get('username')
        if request.FILES.get('avatar'):
            user.avatar = request.FILES.get('avatar')
        if request.POST.get('first_name'):
            user.first_name = request.POST.get('first_name')
        if request.POST.get('last_name'):
            user.last_name = request.POST.get('last_name')
        if request.POST.get('bio'):
            user.bio = request.POST.get('bio')
        if request.POST.get('company_name'):
            user.contractorprofile.company_name = request.POST.get('company_name')
            user.contractorprofile.save()

        user.save()

        messages.add_message(request, messages.SUCCESS, 'User details updated successfully')
        return redirect('dashboard_tab_view', tab='settings')
    else:
        messages.add_message(request, messages.ERROR, '(RequestMethodError): Form could not be saved.')
        return redirect('home')
#############################################################################################################################################


#update staff user and profile data: method only used by staff updating own data
@login_required
def update_staff_details(request):
    if request.method == 'POST':
        user = request.user
        #update db i.e. user and contractor_profile info
        if request.POST.get('username'):
            user.username = request.POST.get('username')
        if request.FILES.get('avatar'):
            user.avatar = request.FILES.get('avatar')
        if request.POST.get('first_name'):
            user.first_name = request.POST.get('first_name')
        if request.POST.get('last_name'):
            user.last_name = request.POST.get('last_name')
        if request.POST.get('bio'):
            user.bio = request.POST.get('bio')
        

        user.save()

        messages.add_message(request, messages.SUCCESS, 'User details updated successfully')
        return redirect('staff_dashboard_section_toggle', section='staff', tab='settings')
    else:
        messages.add_message(request, messages.ERROR, '(RequestMethodError): Form could not be saved.')
        return redirect('home')
#############################################################################################################################################


#change the password
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard_tab_view', tab='settings')
        else:
            messages.error(request, 'Please correct the error below.'+str(form.errors))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



    #Not used
@login_required
def compliance_entry_form(request, record_id):
    form = ComplianceRecordEntryForm()
    record = ComplianceRecord.objects.get(id=record_id)
    compliance_module_types = settings.COMPLIANCE_MODULE_TYPE
    return render(
        request,
        'compliance/create_entry.html',
        {
            'title':'Compliance entry',
            'message':'Create compliance entry',
            'year':datetime.now().year,
            'form':form,
            'record':record,
            'compliance_module_types':compliance_module_types,
            'get_default_objects':get_default_objects(request)
        })
#############################################################################################################################################




#create a new entry and redirect to the record's compliance form
@login_required
def create_compliance_entry(request):
    #check if the entry exists, if yes redirect to edit page else create new record
    if request.method == 'POST':
        form = ComplianceRecordEntryForm(request.POST)
        #get the record
        record = ComplianceRecord.objects.get(id=request.POST.get("record_id"))
        #get module types from settings file
        compliance_module_types = settings.COMPLIANCE_MODULE_TYPE
        if record is not None:
            try:
                #check if its the correct date
                #check if contractor has already subitted a report
                if datetime.now().month-1 == 0:
                    check_entry = ComplianceRecordEntry.objects.get(compliance_record=record, month=12, year=datetime.now().year-1, submitted_by = request.user, is_deleted=False, is_active=True)
                else:
                    check_entry = ComplianceRecordEntry.objects.get(compliance_record=record, month=datetime.now().month-1, year=datetime.now().year, submitted_by = request.user, is_deleted=False, is_active=True)

                if check_entry is not None:
                    messages.add_message(request, messages.ERROR, 'You have already submitted a report. Please wait for feedback.')
                    return redirect('view_entry_report',entry_id=check_entry.id)
                      

            except ComplianceRecordEntry.DoesNotExist:
                #create new entry instance and save
                entry = ComplianceRecordEntry()
                entry.compliance_record = record
                entry.project_name = request.POST.get('project_name')
                entry.created_by = request.user
                entry.last_updated_by = request.user

                #sort out date off by one error
                if datetime.now().month-1 == 0:
                    entry.month = 12
                    entry.year = datetime.now().year-1
                else:
                    entry.month = datetime.now().month -1
                    entry.year = datetime.now().year

                #set as false to mark it as DRAFT
                entry.is_active = False

               #save it
                save = entry.save()

                ###create instances of the forms
                
                #get modules
                modules = ComplianceModule.objects.filter(compliance_record=record)
            
                #create metrics instance
                for module in modules:
                    references =  ComplianceModuleReference.objects.filter(module=module)
                    for reference in references:
                        requirements = ComplianceReferenceRequirement.objects.filter(reference=reference)
                        for requirement in requirements:
                            metrics = ComplianceRequirementMetric.objects.filter(requirement=requirement)
                            for metric in metrics:
                                #create empty metric submissions
                                submission = ComplianceRequirementMetricSubmission()
                                submission.metric = metric
                                submission.created_by = request.user
                                submission.last_updated_by = request.user
                                submission.record_entry = entry
                                submission.save()

                #create personnel instance
                personnel_designations = PersonnelDesignation.objects.filter(record=record)
                for designation in personnel_designations:
                    personnel = Personnel()
                    personnel.record_entry = entry
                    personnel.last_updated_by = request.user
                    personnel.created_by = request.user
                    personnel.designation = designation
                    personnel.save()

                    #success notification
                messages.add_message(request, messages.INFO, 'Complete the forms below and submit the full report for review')
                #redirect to main forms
                return redirect('compliance_form_view',entry_id=entry.id, record_id=record.id)
        
        else:
            messages.add_message(request, messages.ERROR, '(ComplianceRecordNotFoundError): Form could not be initialized.')
            return redirect('home')
   
    else:
        messages.add_message(request, messages.ERROR, '(RequestMethodError): Form could not be initialized.')
        return redirect('home')
#############################################################################################################################################


#create a copy of complliance form | continue editing from last month's report
@login_required
def create_entry_from_previous(request):
    #check if the entry exists, if yes redirect to edit page else create new record
    if request.method == 'POST':
        form = ComplianceRecordEntryForm(request.POST)
        #get previous entry
        p_entry = ComplianceRecordEntry.objects.get(id=request.POST.get("entry_id"))
        #get module types
        compliance_module_types = settings.COMPLIANCE_MODULE_TYPE
        if p_entry is not None:
                #create new compliance entry
                new_entry = ComplianceRecordEntry()
                #copy data from Previous entry to new entry
                new_entry.compliance_record = p_entry.compliance_record
                new_entry.project_name = p_entry.project_name
                new_entry.created_by = request.user
                new_entry.last_updated_by = request.user
                
                #check off by 1 error for date
                if datetime.now().month-1 == 0:
                    new_entry.month = 12
                    new_entry.year = datetime.now().year-1
                else:
                    new_entry.month = datetime.now().month -1
                    new_entry.year = datetime.now().year

                #set as false to keep it as draft
                new_entry.is_active = False
                new_entry.save()

                #register inheritance record
                inheritance = EntryInheritance()
                inheritance.child = new_entry
                inheritance.parent = p_entry
                inheritance.created_by = request.user
                inheritance.save()

                
                #get previous  personnel submissions
                prev_personnel = Personnel.objects.filter(record_entry=p_entry)
                
                #transfer personnel to new entry
                if prev_personnel:
                    
                    for p_personnel in prev_personnel:
                        new_personnel = Personnel()
                        new_personnel.record_entry = new_entry
                        new_personnel.last_updated_by = request.user
                        new_personnel.created_by = request.user
                        new_personnel.designation = p_personnel.designation
                        new_personnel.first_name = p_personnel.first_name
                        new_personnel.other_name = p_personnel.other_name
                        new_personnel.email = p_personnel.email
                        new_personnel.tel_number = p_personnel.tel_number
                        new_personnel.save()
                    
                        #get personnel documents
                        prev_personnel_documents = PersonnelDocument.objects.filter(personnel=p_personnel,is_deleted=False)
                        #transfer documents to new entry
                        if prev_personnel_documents is not None:
                            for prev_personnel_document in prev_personnel_documents:
                                new_personnel_document = PersonnelDocument()
                                new_personnel_document.personnel = new_personnel
                                new_personnel_document.description = prev_personnel_document.description
                                new_personnel_document.type = prev_personnel_document.type
                                new_personnel_document.attachment = prev_personnel_document.attachment
                                new_personnel_document.is_deleted = prev_personnel_document.is_deleted
                                new_personnel_document.created_by = request.user
                                new_personnel_document.last_updated_by = request.user
                                new_personnel_document.save()



                #get previous submissions
                prev_submissions = ComplianceRequirementMetricSubmission.objects.filter(record_entry=p_entry)
                if prev_submissions is not None:
                    for p_submission in prev_submissions:
                        #transfer metric submissions
                        new_submission = ComplianceRequirementMetricSubmission()
                        new_submission.metric = p_submission.metric
                        new_submission.notes = p_submission.notes
                        new_submission.created_by = request.user
                        new_submission.last_updated_by = request.user
                        new_submission.record_entry = new_entry
                        new_submission.save()

                #previous requirement attachment submissions
                prev_requirement_attachments = ComplianceRequirementAttachmentSubmission.objects.filter(record_entry=p_entry, is_deleted=False)
                #transfer attachments to new entry
                if prev_requirement_attachments is not None:
                    for prev_requirement_attachment in prev_requirement_attachments:
                        new_requirement_attachment = ComplianceRequirementAttachmentSubmission()
                        new_requirement_attachment.record_entry = new_entry
                        new_requirement_attachment.requirement_detail = prev_requirement_attachment.requirement_detail
                        new_requirement_attachment.attachment = prev_requirement_attachment.attachment
                        new_requirement_attachment.last_updated_by = prev_requirement_attachment.last_updated_by
                        new_requirement_attachment.is_deleted = prev_requirement_attachment.is_deleted
                        new_requirement_attachment.save()

                #flash message and redirect to form view
                messages.add_message(request, messages.SUCCESS, 'Data copied successfully, continue updating. Dont forget to check feedback from previous report before submitting your report.')
                return redirect('compliance_form_view',entry_id=new_entry.id, record_id=new_entry.compliance_record.id)

        else:
            messages.add_message(request, messages.ERROR, '(ComplianceRecordNotFoundError): Form could not be initialized.')
            return redirect('home')
   
    else:
        messages.add_message(request, messages.ERROR, '(RequestMethodError): Form could not be initialized.')
        return redirect('home')
#############################################################################################################################################
           
                




#compliance form view:: display view dependnig on the parameters given:: toDo== include ajax filter for UX improvement
@login_required
def compliance_form_view(request, entry_id, record_id,message=None):
    record = ComplianceRecord.objects.get(id=record_id)
    #get entry instance
    entry = ComplianceRecordEntry.objects.get(id=entry_id, compliance_record=record)

    compliance_module_types = settings.COMPLIANCE_MODULE_TYPE

    #security check - I however doubt the last_updated_by condition
    if entry.last_updated_by == request.user or entry.created_by == request.user or request.user.is_admin:
        return render(
            request,
            'compliance/create_entry.html',
            {
                'title':'Compliance entry',
                'message':'Create compliance entry',
                'year':datetime.now().year,
                'record':record,
                'entry':entry,
                'compliance_module_types':compliance_module_types,
                'get_default_objects':get_default_objects(request),
            
            })
    else:
        messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): Form could not be loaded.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################


#select reference from the form list
@login_required
def compliance_reference_select(request, entry_id, record_id, reference_id):
    record = ComplianceRecord.objects.get(id=record_id)
    entry = ComplianceRecordEntry.objects.get(id=entry_id, compliance_record=record)
    reference = ComplianceModuleReference.objects.get(id=reference_id)
    requirements = ComplianceReferenceRequirement.objects.filter(reference=reference)
    personnel_form = PersonnelForm()
    personnel_document_form = PersonnelDocumentForm()
    compliance_module_types = settings.COMPLIANCE_MODULE_TYPE

    if entry.last_updated_by == request.user or entry.created_by == request.user or request.user.is_admin:
        return render(
            request,
            'compliance/create_entry.html',
            {
                'title':'Compliance references',
                'message':'Select compliance references',
                'year':datetime.now().year,
                'entry':entry,
                'record':record,
                'reference':reference,
                'compliance_module_types':compliance_module_types,
                'get_default_objects':get_default_objects(request)
            })

    else:
        messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): Form could not be loaded.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#this reveals personnel destinations
@login_required
def compliance_personnel_select(request, entry_id, record_id):
    record = ComplianceRecord.objects.get(id=record_id)
    entry = ComplianceRecordEntry.objects.get(id=entry_id, compliance_record=record)
    personnel = Personnel.objects.filter(record_entry=entry)
    personnel_form = PersonnelForm()
    personnel_document_form = PersonnelDocumentForm()
    form = ComplianceRecordEntryForm()
    compliance_module_types = settings.COMPLIANCE_MODULE_TYPE

    if entry.last_updated_by == request.user or entry.created_by == request.user or request.user.is_admin:

        return render(
            request,
            'compliance/create_entry.html',
            {
                'title':'Compliance entry',
                'message':'Create compliance entry',
                'year':datetime.now().year,
                'entry':entry,
                'record':record,
                'personnel':personnel,
                'form':form,
                'compliance_module_types':compliance_module_types,
                'get_default_objects':get_default_objects(request)
            })

    else:
        messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): Form could not be loaded.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################


@login_required
def compliance_requirement_view(request, entry_id, record_id, reference_id, requirement_id):
    #get the requirement and the coreresponding attachment requirements
    record = ComplianceRecord.objects.get(id=record_id)
    entry = ComplianceRecordEntry.objects.get(id=entry_id, compliance_record=record)
    reference = ComplianceModuleReference.objects.get(id=reference_id)
    requirement = ComplianceReferenceRequirement.objects.get(id=requirement_id)
    attachment_detail = ComplianceRequirementAttachmentDetails.objects.get(requirement=requirement)
    personnel_form = PersonnelForm()
    personnel_document_form = PersonnelDocumentForm()
    compliance_module_types = settings.COMPLIANCE_MODULE_TYPE

    
    attachment_submissions = ComplianceRequirementAttachmentSubmission.objects.filter(record_entry=entry,requirement_detail=attachment_detail, is_deleted=False)
    submission_form = ComplianceRequirementMetricSubmissionForm()

    #security check
    if entry.last_updated_by == request.user or entry.created_by == request.user or request.user.is_admin:

        return render(
            request,
            'compliance/create_entry.html',
            {
                'title':'Compliance requirements',
                'message':'Create compliance requirements',
                'year':datetime.now().year,
                'entry':entry,
                'record':record,
                'reference':reference,
                'requirement':requirement,
                'attachment_submissions':attachment_submissions,
                'compliance_module_types':compliance_module_types,
                'get_default_objects':get_default_objects(request)
            })

    else:
        messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): Form could not be loaded.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#get personnel form
@login_required
def compliance_personnel_view(request, entry_id, record_id, personnel_id):
    #get the corresponding personnel from the entry
    record = ComplianceRecord.objects.get(id=record_id)
    entry = ComplianceRecordEntry.objects.get(id=entry_id, compliance_record=record)
    person = Personnel.objects.get(id=personnel_id)
    personnel_attachments = PersonnelDocument.objects.filter(personnel=person)
    personnel_form = PersonnelForm(instance=person)
    personnel_document_form = PersonnelDocumentForm()
    compliance_module_types = settings.COMPLIANCE_MODULE_TYPE
    personnel = Personnel.objects.filter(record_entry=entry)
    
    #security check
    if entry.last_updated_by == request.user or entry.created_by == request.user or request.user.is_admin:

        return render(
            request,
            'compliance/create_entry.html',
            {
                'title':'Compliance entry',
                'message':'Create compliance entry',
                'year':datetime.now().year,
                'entry':entry,
                'record':record,
                'person':person,
                'personnel':personnel,
                'personnel_attachments':personnel_attachments,
                'personnel_form':personnel_form,
                'personnel_document_form':personnel_document_form,
                'compliance_module_types':compliance_module_types,
                'get_default_objects':get_default_objects(request)
            })
    else:
        messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): Form could not be loaded.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################


#update pesonnel details
@login_required
def update_personnel_details(request):
    if request.method == "POST":
        if request.user.is_contractor or request.user.is_projectmanager or request.user.is_admin:
            if request.POST.get("entry_id") and request.POST.get("personnel_id"):
                entry = ComplianceRecordEntry.objects.get(id=request.POST.get("entry_id"))
                person = Personnel.objects.get(id=request.POST.get("personnel_id"))
                personnel_attachment = PersonnelDocumentForm(request.POST, request.FILES)

                if entry.is_published == False:

                    if request.POST.get("first_name"):
                        person.first_name = request.POST.get("first_name")

                    if request.POST.get("other_name"):
                        person.other_name = request.POST.get("other_name")

                    if request.POST.get("email"):
                        person.email = request.POST.get("email")

                    if request.POST.get("tel_number"):
                        person.tel_number = request.POST.get("tel_number")

                    person.save()

                    if request.FILES.get("attachment"):
                        if personnel_attachment.is_valid() and person is not None:
                            attachment = personnel_attachment.save(commit=False)
                            attachment.personnel = person
                            attachment.created_by = request.user
                            attachment.last_updated_by = request.user
                            attachment.save()

                    messages.add_message(request, messages.SUCCESS, 'Personnel data saved successfully.')
                    return redirect('compliance_personnel_view', 
                                entry_id=entry.id,
                                record_id=entry.compliance_record.id,
                                personnel_id=person.id,
                                )

                else:
                    messages.add_message(request, messages.ERROR, '(WritePermissionError): Form could not be edited. The report has already been published by PPDC. Please wait for the next submission period or contact KoTDA ICT Office for support.')
                    return redirect('home')

        else:
            messages.add_message(request, messages.ERROR, '(RequestPermissionError): Form could not be saved. You do not have the correct rights')
            return redirect('home')
    else:
        messages.add_message(request, messages.ERROR, '(RequestMethodError): Form could not be saved.')
        return redirect('home')
#############################################################################################################################################



#create extra personnel
@login_required
def create_extra_personnel(request):
    if request.method == "POST":
        if request.POST.get("entry_id"):
            entry = ComplianceRecordEntry.objects.get(id=request.POST.get("entry_id"))
            designation_form = PersonnelDesignationForm(request.POST)
            if entry.is_published == False and entry.created_by == request.user:
                try:
                    if request.POST.get("type"):
                    
                        designation = designation_form.save(commit=False)
                        designation.record = entry.compliance_record
                        designation.is_extra = True
                        designation.save()

                        personnel = Personnel()
                        personnel.record_entry = entry
                        personnel.designation = designation
                        personnel.first_name = request.POST.get("first_name")
                        personnel.other_name = request.POST.get("other_name")
                        personnel.email = request.POST.get("email")
                        personnel.tel_number = request.POST.get("tel_number")
                        personnel.created_by = request.user
                        personnel.last_updated_by = request.user
                        personnel.save()

                        attachment_form = PersonnelDocumentForm(request.POST, request.FILES)
                        if attachment_form.is_valid():
                            attachment = attachment_form.save(commit=False)
                            attachment.personnel = personnel
                            attachment.created_by = request.user
                            attachment.last_updated_by = request.user
                            attachment.save()

                        messages.add_message(request, messages.SUCCESS, 'Personnel data saved successfully.')
                        return redirect('compliance_personnel_view', 
                                entry_id=entry.id,
                                record_id=entry.compliance_record.id,
                                personnel_id=personnel.id,
                                )
                except:
                    messages.add_message(request, messages.ERROR, '(ExceptionError): Form could not be saved.')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            else:
                messages.add_message(request, messages.ERROR, '(WritePermissionError): Form could not be edited. The report has already been published by PPDC. Please wait for the next submission period or contact KoTDA ICT Office for support.')
                return redirect('home')
    else:
        messages.add_message(request, messages.ERROR, '(RequestMethodError): Form could not be saved.')
        return redirect('home')
#############################################################################################################################################


#delete personnel attachment
@login_required
def delete_personnel_attachment(request, document_id):
    document = PersonnelDocument.objects.get(id=document_id)
    if document.last_updated_by == request.user or document.created_by == request.user:
        if document is not None:
            document.is_deleted = True
            document.last_updated_by = request.user
            document.save()

            messages.add_message(request, messages.SUCCESS, 'Document deleted successfully')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    messages.add_message(request, messages.ERROR, '(ACCESS_DENIED):Document could not be deleted.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################


#delete requirement attachment
@login_required
def delete_requirement_attachment(request, document_id):
    document = ComplianceRequirementAttachmentSubmission.objects.get(id=document_id)
    if document.last_updated_by == request.user or document.created_by == request.user:
        if document is not None:
            document.is_deleted = True
            document.last_updated_by = request.user
            document.save()


            messages.add_message(request, messages.SUCCESS, 'Document deleted successfully')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.add_message(request, messages.ERROR, '(ACCESS_DENIED):Document could not be deleted.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#not used TODO:improve on it
@login_required
def download_requirement_attachment(request, document_id):
    document = ComplianceRequirementAttachmentSubmission.objects.get(id=document_id)
    if document is not None:
        BASE = os.path.dirname(os.path.dirname(__file__))
        zip_file = open(os.path.dirname(settings.MEDIA_ROOT, document.attachment.url), 'r')
        response = HttpResponse(zip_file, content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename="%s"' % 'foo.zip'
        return response

    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#update metric submission
@login_required
def update_compliance_entry(request):
    if request.method == 'POST':
    
        if request.POST.get("entry_id"):
            entry = ComplianceRecordEntry.objects.get(id=request.POST.get("entry_id"))
            #check if it's the right person updating the form | published reports can not be edited
            if entry.created_by != request.user or entry.is_published == True:
                messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): You do not have permission to edit this record.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            #get attachments
            attachment = request.FILES.get('attachment', None)
            modules = ComplianceModule.objects.filter(compliance_record=entry.compliance_record)
            reference = ComplianceModuleReference.objects.get(id=request.POST.get("reference_id"))
            requirement = ComplianceReferenceRequirement.objects.get(id=request.POST.get("requirement_id"))
            submissions = ComplianceRequirementMetricSubmission.objects.filter(record_entry=entry)

                

            
            #update metrics
            counter = [0,1,2,3,4,5,6]#TODO:maybe a better iterator would be appropriate
            for count in counter:
                if request.POST.getlist('metric_id['+str(count)+']') and request.POST.getlist('submission_id['+str(count)+']') and request.POST.getlist('notes['+str(count)+']'): 
                    
                    try:
                       
                        for submission in request.POST.getlist('submission_id['+str(count)+']'):
                            sub= ComplianceRequirementMetricSubmission.objects.get(id=submission)
                            for note in request.POST.getlist('notes['+str(count)+']'):
                                if request.POST.getlist('notes['+str(count)+']').index(note) == request.POST.getlist('submission_id['+str(count)+']').index(submission):
                                   
                                    sub.notes = note
                                    sub.last_updated_by = request.user
                                    sub.save()
                                    
                                    #update entry model
                                    entry.last_updated_by = request.user
                                    entry.save()
                                

                    except:
                        #raise Exception(request.POST)
                        messages.add_message(request, messages.ERROR, '(ExceptionError): Form could not be saved.')
                        return redirect('compliance_requirement_view', 
                            entry_id=entry.id,
                            record_id=entry.compliance_record.id,
                            reference_id=reference.id,
                            requirement_id=requirement.id
                            )

            #not used. alternative attachment upload logic
            if attachment is not None:
                try:
                    attachment_detail = ComplianceRequirementAttachmentDetails.objects.get(id=request.POST.get("attachment_detail_id"))
                    att = ComplianceRequirementAttachmentSubmission()
                    att.requirement_detail = attachment_detail
                    att.record_entry = entry
                    att.attachment = attachment
                    att.last_updated_by = request.user
                    att.save()

                    #update entry model
                    entry.last_updated_by = request.user
                    entry.save()
                except:
                    messages.add_message(request, messages.ERROR, 'Upload save error')
                    
                   
            messages.add_message(request, messages.SUCCESS, 'Save successful')
            return redirect('compliance_requirement_view', 
                entry_id=entry.id,
                record_id=entry.compliance_record.id,
                reference_id=reference.id,
                requirement_id=requirement.id
                )

        else:
            messages.add_message(request, messages.ERROR, '(RecordNotFoundError): Compliance record could not be found. Contact KoTDA ICT for support.')
            return redirect('home')
#############################################################################################################################################


#list draft monthly reports
@login_required
def list_draft_reports(request, record_id):
    record = ComplianceRecord.objects.get(id=record_id)
    entries = ComplianceRecordEntry.objects.filter(compliance_record=record, is_deleted=False, is_published=False, is_active=False, last_updated_by=request.user).order_by('-id')

    return render(
        request,
        'compliance/list_report_view.html',
        {
            'title':'Compliance report draft list',
            'message':'monthly report draft list',
            'year':datetime.now().year,
            'entries':entries,
            'record':record,
            'get_default_objects':get_default_objects(request)
        })
#############################################################################################################################################


#list user all submitted monthly reports
@login_required
def list_mysubmitted_reports(request, record_id):
    record = ComplianceRecord.objects.get(id=record_id)
    entries = ComplianceRecordEntry.objects.filter(compliance_record=record, is_deleted=False, is_active=True, created_by=request.user).order_by('-id')

    return render(
        request,
        'compliance/list_report_view.html',
        {
            'title':'Compliance report draft list',
            'message':'monthly report draft list',
            'year':datetime.now().year,
            'entries':entries,
            'record':record,
            'get_default_objects':get_default_objects(request)
        })
#############################################################################################################################################


#list all published monthly reports
@login_required
def list_submitted_reports(request, record_id):
    if  request.user.is_admin or request.user.is_staff:
        record = ComplianceRecord.objects.get(id=record_id)
        entries = ComplianceRecordEntry.objects.filter(compliance_record=record, is_deleted=False, is_active=True).order_by('-id')

        return render(
            request,
            'compliance/list_report_view.html',
            {
                'title':'Compliance report all submitted list',
                'message':'monthly report draft list',
                'year':datetime.now().year,
                'entries':entries,
                'record':record,
                'get_default_objects':get_default_objects(request)
            })
    else:
        messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): You do not have permission to view this resource.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################


#all acknowledged reports
@login_required
def list_acknowledged_reports(request, record_id):
    if request.user.is_admin or request.user.is_staff:
        record = ComplianceRecord.objects.get(id=record_id)
        entries = ComplianceRecordEntry.objects.filter(compliance_record=record, is_deleted=False, is_active=True, is_published=True).order_by('-id')

        return render(
            request,
            'compliance/list_report_view.html',
            {
                'title':'Compliance report draft list',
                'message':'monthly report draft list',
                'year':datetime.now().year,
                'entries':entries,
                'record':record,
                'get_default_objects':get_default_objects(request)
            })

    else:
        messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): You do not have permission to view this resource.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#TODO:my acknowledged reports
@login_required
def list_myacknowledged_reports(request, record_id):
    record = ComplianceRecord.objects.get(id=record_id)
    entries = ComplianceRecordEntry.objects.filter(compliance_record=record, is_deleted=False, is_active=True, is_published=True, created_by=request.user).order_by('-id')

    return render(
        request,
        'compliance/list_report_view.html',
        {
            'title':'Compliance report draft list',
            'message':'monthly report draft list',
            'year':datetime.now().year,
            'entries':entries,
            'record':record,
            'get_default_objects':get_default_objects(request)
        })
#############################################################################################################################################


#delete entry
@login_required
def delete_entry(request, entry_id):
    entry = ComplianceRecordEntry.objects.get(id=entry_id)
    if entry is not None:
        #only the originator can delete a report so long as its a draft
        if entry.created_by == request.user and entry.is_published == False:
            entry.is_deleted = True#set to true
            entry.is_published = False
            entry.is_rejected = False
            entry.last_updated_by = request.user
            entry.deleted_by = request.user#mark this guy
            entry.status = 'deleted'
            entry.save()
            messages.add_message(request, messages.SUCCESS, 'Record deleted successfully')
        else:
            messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): You do not have permission to delete this resource.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################


#raise a noncompliance issue on a requirement submission
#todo:improve on the javascript responses
@login_required
def raise_noncompliance_issue(request):
    if request.method == 'POST':
        entry = ComplianceRecordEntry.objects.get(id=request.POST.get('entry_id'))
        requirement = ComplianceReferenceRequirement.objects.get(id=request.POST.get('requirement_id'))
        notes = request.POST.get('notes')

        if notes and requirement and entry is not None:
            if request.user.is_staff or request.user.is_admin:
                #save the note
                issue = ComplianceRequirementIssue()
                issue.entry = entry
                issue.requirement = requirement
                issue.notes = notes
                issue.is_resolved = False
                issue.last_updated_by = request.user
                issue.save()

                success = "message sent successfully"
                messages.add_message(request, messages.SUCCESS, 'Issue submitted successfully')
                return HttpResponse(issue.notes)
                #return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                
            else:
                fail="message not sent"
                messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): You do not have permission to access this resource.')
                return HttpResponse(fail)
                #return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        messages.add_message(request, messages.ERROR, '(ERROR): Could not submit issue. Please contact KoTDA ICT support for assistance')       
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#raise a noncompliance issue on a personnel submission
@login_required
def raise_personnel_noncompliance_issue(request):
    if request.method == 'POST':
        entry = ComplianceRecordEntry.objects.get(id=request.POST.get('entry_id'))
        personnel = Personnel.objects.get(id=request.POST.get('personnel_id'))
        notes = request.POST.get('notes')

        if notes and personnel and entry is not None:
            if request.user.is_staff or request.user.is_admin:
                #save the note
                issue = CompliancePersonnelIssue()
                issue.entry = entry
                issue.personnel = personnel
                issue.notes = notes
                issue.is_resolved = False
                issue.last_updated_by = request.user
                issue.save()
                messages.add_message(request, messages.SUCCESS, 'Issue submitted successfully')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            #todo:- send email to contractor on the 20th about the issue
            else:
                messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): You do not have permission to access this resource.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        messages.add_message(request, messages.ERROR, '(ERROR): Could not submit issue. Please contact KoTDA ICT support for assistance')       
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################


#remove non compliance issue
@login_required
def delete_noncompliance_issue(request, issue_id):
    issue = ComplianceRequirementIssue.objects.get(id=issue_id)
    if issue is not None:
        if request.user.is_staff or request.user.is_admin:
            issue.is_deleted = True
            issue.last_updated_by = request.user
            issue.save()
            messages.add_message(request, messages.SUCCESS, 'Issue removed successfully')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): You do not have permission to access this resource.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    messages.add_message(request, messages.ERROR, '(ERROR): Could not submit issue. Please contact KoTDA ICT support for assistance')       
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################


#remove personnel non compliance issue
@login_required
def delete_personnel_noncompliance_issue(request, issue_id):
    issue = CompliancePersonnelIssue.objects.get(id=issue_id)
    if issue is not None:
        if request.user.is_staff or request.user.is_admin:
            issue.is_deleted = True
            issue.last_updated_by = request.user
            issue.save()
            messages.add_message(request, messages.SUCCESS, 'Issue removed successfully')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): You do not have permission to access this resource.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    messages.add_message(request, messages.ERROR, '(ERROR): Could not submit issue. Please contact KoTDA ICT support for assistance')       
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#acknowledge reciept of an entry
###todo:Add level of access for staff
@login_required
def acknowledge_entry(request):
    if request.method == 'POST':
        entry = ComplianceRecordEntry.objects.get(id=request.POST.get('entry_id'))
        entry_form = ComplianceRecordEntryForm(instance=entry)
        acknowledgement = request.POST.get('is_acknowledged')
        
        if request.user.is_manager or request.user.is_teamlead or request.user.is_admin:
            if acknowledgement and entry is not None:
                #set to is_published = true
                review = request.POST.get('review')

                if request.POST.get('accept'):
                    entry.is_published = True
                    entry.is_rejected = False
                    entry.is_active = True
                    entry.status = 'acknowledged'
                    entry.evaluated_by = request.user
                elif request.POST.get('reject'):
                    entry.is_published = False
                    entry.is_rejected = True
                    entry.is_active = True
                    entry.status = 'rejected'
                    entry.evaluated_by = request.user

                if review:
                    entry.review = review
                    entry.is_published_with_comments = True
                else:
                    entry.is_published_with_comments = False
                entry.save()

                try:

                    if entry.is_published_with_comments == True:
                        surfix = "with comments."+".-- "+str(entry.review)
                    else:
                        surfix = "."

                    #send email
                    if entry.status == 'acknowledged':
                        message = "The Compliance report on "+ str(entry.compliance_record.type) + " for period " + str(entry.month) +"/" + str(entry.year)+  " has been acknowledged " +str(surfix)
                        subject="Acknowledged Receipt of Compliance Report"
                        #flash notification
                        messages.add_message(request, messages.SUCCESS, 'Report acknowledged successfully ')
                    elif entry.status == 'rejected':
                        message = "The Compliance report on "+ str(entry.compliance_record.type) + " for period " + str(entry.month) +"/" + str(entry.year)+  " has been rejected "+str(surfix)
                        subject="Compliance Report Rejected"
                        #flash notification
                        messages.add_message(request, messages.SUCCESS, 'Report rejected successfully')
                    send_email_task.delay(
                        to=entry.created_by.email,
                        subject=subject,
                        message=message)

                    msg_html = render_to_string('compliance/emails/submission_reminder.html',
                                                    {'subject': subject,
                                                    'message':message,
                                                    'contractor':entry.created_by,
                                                    'entry':entry,
                                                    })
          
                    send_mail(
                        subject,
                        msg_html,
                        settings.EMAIL_HOST_USER,
                        [entry.created_by.email, request.user.email, 'ppd-c@konza.go.ke'],
                        html_message=msg_html,
                        fail_silently=False,
                    )
                except:
                    pass

            
                return redirect('view_entry_report',entry_id=entry.id)

        else:
            messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): You do not have permission to access this resource.')      
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.add_message(request, messages.ERROR, '(RequestMethodError): Data could not be saved.')
        return redirect('home')
#############################################################################################################################################



#view entry report
@login_required
def view_entry_report(request, entry_id):
    entry = ComplianceRecordEntry.objects.get(id=entry_id)
    entry_form = ComplianceRecordEntryForm(instance=entry)

    if entry is not None:
        #security check
        if entry.last_updated_by == request.user or entry.created_by == request.user or request.user.is_admin or request.user.is_staff:

            return render(
                request,
                'compliance/report_view.html',
                {
                    'title':'Compliance report view',
                    'message':' report view',
                    'year':datetime.now().year,
                    'entry':entry,
                    'entry_form':entry_form,
                    'get_default_objects':get_default_objects(request)
                })
        else:
            messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): You do not have permission to access this resource.')      
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
            return redirect('home')
#############################################################################################################################################



#view module report
@login_required
def view_entry_module_report(request, entry_id, module_id):
    entry = ComplianceRecordEntry.objects.get(id=entry_id)
    module = ComplianceModule.objects.get(id=module_id)
    entry_form = ComplianceRecordEntryForm(instance=entry)
  
    if entry is not None:
        #security check
        if entry.last_updated_by == request.user or entry.created_by == request.user or request.user.is_admin or request.user.is_staff:
            return render(
                request,
                'compliance/report_view.html',
                {
                    'title':'Compliance report view',
                    'message':' report view',
                    'year':datetime.now().year,
                    'entry':entry,
                    'module':module,
                    'entry_form':entry_form,
                    'get_default_objects':get_default_objects(request)
                })
        else:
            messages.add_message(request, messages.ERROR, '(ACCESS_DENIED): You do not have permission to access this resource.')      
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
            return redirect('home')
#############################################################################################################################################



        #submit an entry
@login_required
def submit_report_entry(request):
    if request.method == 'POST':
        if request.POST.get("entry_id"):
            entry = ComplianceRecordEntry.objects.get(id=request.POST.get("entry_id"))
            
            #check if an entry has already been sent
            try:

            #check if contractor has already subitted a report
                if datetime.now().month-1 == 0:
                    check_entry = ComplianceRecordEntry.objects.get(compliance_record=entry.compliance_record, month=12, year=datetime.now().year-1, submitted_by = request.user, is_deleted=False, is_active=True)
                else:
                    check_entry = ComplianceRecordEntry.objects.get(compliance_record=entry.compliance_record, month=datetime.now().month-1, year=datetime.now().year, submitted_by = request.user, is_deleted=False, is_active=True)

                if check_entry is not None:
                    messages.add_message(request, messages.ERROR, 'You have already submitted a report for the month. Please wait for feedback.')
                    return redirect('view_entry_report',entry_id=check_entry.id)
                 
            except:
                pass


            #check if an contractor account has been blocked
            try:

                contractor_profile = ContractorProfile.objects.get(id=request.user.id)
                if contractor_profile.is_blocked == True:
                    messages.add_message(request, messages.ERROR, 'Report submission failed. This account has been blocked by PPDC for non-compliance.')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                
            except:
                pass


            #security check
            if request.user == entry.created_by and request.user.is_projectmanager:
            #check if all fields have been filled correctly

                if request.POST.get("is_acknowledged"):
                    entry.is_active = True
                    entry.status = 'pending'
                    entry.is_published = False
                    entry.is_rejected = False
                    if request.POST.get('summary'):
                        entry.summary = request.POST.get('summary')
                    entry.submitted_by = request.user
                    entry.submitted_at = datetime.now()
                    entry.save()
                    messages.add_message(request, messages.SUCCESS, 'Report submitted successfully. Please wait for feedback from PPDC')


                    try:
                        #send email
                        message = "The Compliance report on "+ str(entry.compliance_record.type) + " for period " + str(entry.month) +"/" + str(entry.year)+  " has been submitted successfully. Please wait for feedback from PPDC"
                        subject="Successful Submit Compliance Report"
                       
                        send_email_task.delay(
                        to=entry.last_updated_by.email,
                        subject=subject,
                        message=message)

                        #send email
              #          msg_plain = render_to_string('compliance/report_email.txt', {'entry': entry})
              #          msg_html = render_to_string('compliance/report_download.html', {'entry': entry})
              #
              #          send_mail(
              #              'email title',
              #              msg_plain,
              #              settings.EMAIL_HOST_USER,
              #              [request.user.email],
              #              html_message=msg_html,
              #          )


                        msg_html = render_to_string('compliance/emails/submission_reminder.html',
                                                    {'subject': subject,
                                                    'message':message,
                                                    'contractor':request.user
                                                    })
          
                        send_mail(
                            subject,
                            msg_html,
                            settings.EMAIL_HOST_USER,
                            [request.user.email,"ppc@konza.go.ke"],
                            html_message=msg_html,
                            fail_silently=False,
                        )
                    except:
                        pass
                else:
                    messages.add_message(request, messages.ERROR, '(RequestMethodError): Data could not be submitted.')
                    return redirect('dashboard_view')


        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#list contactors
@login_required
def list_contactors(request):
    contractors = User.objects.filter(is_contractor=True,is_active=True,is_admin=False)
    return render(
        request,
        'compliance/user_list.html',
        {
            'title':'Compliance Report: Contractor list',
            'message':'list of contractors successful',
            'year':datetime.now().year,
            'contractors':contractors,
            'get_default_objects':get_default_objects(request)
        })
#############################################################################################################################################



#todo:-search for entry
@login_required
def search_entry(request, key):
    pass
     
#############################################################################################################################################



#todo:-view contractor profile
@login_required
def contractor_profile(request, contractor_id, tab=''):
    records = ComplianceRecord.objects.filter(is_deleted=False)
    contractor = User.objects.get(id=contractor_id) or None
    if contractor != None:
        #security check
        if request.user.is_staff or request.user.is_admin or request.user == contractor:
            return render(
                request,
                'compliance/view_profile.html',
                {
                    'title':'Compliance | Contractor profile',
                    'message':'Manage your reports',
                    'year':datetime.now().year,
                    'tab':tab,
                    'records':records,
                    'contractor':contractor,
                    'get_default_objects':get_default_objects(request)
                }
    
            )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################

     


#download report page
@login_required
def report_download(request, entry_id):
    entry = ComplianceRecordEntry.objects.get(id=entry_id)

    
    template = Template('compliance/report_download.html')
    context = Context({
        "entry": entry,
    })
    html = template.render(context)
    pdf = render_to_pdf('compliance/report_download.html', {"entry": entry,})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Report_%s.pdf" %(str(entry.month)+"_ "+str(entry.year))
        content = "inline; filename=%s" %(filename)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename=%s" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")
#############################################################################################################################################



#staff dashboard
@login_required
def staff_dashboard(request, user_id):
    user = User.objects.get(id=user_id)#unused???
    records = ComplianceRecord.objects.filter(is_deleted=False, is_active=True)
    
    if request.user.is_staff or request.user.is_admin:
        return render(
            request,
            'compliance/staff_dashboard.html',
            {
                'title':'Compliance Report: Staff Dashboard',
                'year':datetime.now().year,
                'section':'staff',
                'tab':'staff',
                'records':records,
                'get_default_objects':get_default_objects(request)
            })
    else:
        messages.add_message(request, messages.ERROR, '(PermissionError): This resource is restricted.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



@login_required
def staff_dashboard_section_toggle(request, section='staff', tab=None):
    
    records = ComplianceRecord.objects.filter(is_deleted=False, is_active=True)
    
    if tab == 'pending':
        entries = ComplianceRecordEntry.objects.filter(is_published=False, is_deleted=False, is_active=True).order_by('-id')
    elif tab == 'acknowledged':
        entries = ComplianceRecordEntry.objects.filter(is_published=True, is_deleted=False, is_active=True).order_by('-id') or None
    elif tab == 'rejected':
        entries = ComplianceRecordEntry.objects.filter(is_rejected=True, is_deleted=False, is_active=True).order_by('-id') or None
    elif tab == 'settings':
        entries = ComplianceRecordEntry.objects.filter(is_deleted=False, is_active=True).order_by('-id') or None
    elif tab == 'contractors':
        entries = ComplianceRecordEntry.objects.filter( is_deleted=False, is_active=True).order_by('-id') or None
    else:
        entries = []


    if request.user.is_staff or request.user.is_admin:
        return render(
            request,
            'compliance/staff_dashboard.html',
            {
                'title':'Compliance Report: Staff Dashboard',
                'year':datetime.now().year,
                'section':section,
                'tab':tab,
                'records':records,
                'entries':entries,
                'get_default_objects':get_default_objects(request)
            })
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#appoint / fire teamlead
@login_required
def appoint_teamlead(request):
    if request.method == 'POST':
        #check if its the right guy appointing. only a manager can do this
        if request.user.is_manager or request.user.is_admin:
            
            staff = User.objects.get(id=request.POST.get('staff_id'))

            if staff == request.user:
                messages.add_message(request, messages.ERROR, '(PermissionError): Staff could not be updated successfully. You do not have enough priviledges. Contact ICToffice for assistance')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
           
            if request.POST.get('is_teamlead'):
                staff.is_teamlead = True
            elif not request.POST.get('is_teamlead'):
                staff.is_teamlead = False
            staff.save()

            messages.add_message(request, messages.SUCCESS, 'Staff priviledges updated successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.add_message(request, messages.ERROR, '(PermissionError): Staff could not be updated successfully. You do not have enough priviledges.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################

        

#staff dashboard by tab
@login_required
def staff_dashboard_tab(request, user_id, tab):
    user = User.objects.get(id=user_id)
    records = ComplianceRecord.objects.filter(is_deleted=False, is_active=True)
   
   #check for the tab
    if tab == 'pending':
        entries = ComplianceRecordEntry.objects.filter(is_published=False, is_deleted=False, is_active=True).order_by('-id')
    elif tab == 'acknowledged':
        entries = ComplianceRecordEntry.objects.filter(is_published=True, is_deleted=False, is_active=True).order_by('-id') or None
    elif tab == 'rejected':
        entries = ComplianceRecordEntry.objects.filter(is_rejected=True, is_deleted=False, is_active=True).order_by('-id') or None
    elif tab == 'settings':
        entries = ComplianceRecordEntry.objects.filter(is_deleted=False, is_active=True).order_by('-id') or None
    elif tab == 'contractors':
        entries = ComplianceRecordEntry.objects.filter( is_deleted=False, is_active=True).order_by('-id') or None

    elif tab == 'staff':
        entries = ComplianceRecordEntry.objects.filter( is_deleted=False, is_active=True).order_by('-id') or None
    elif tab == 'pending_tl_inspection':
        entries = ComplianceRecordEntry.objects.filter( is_deleted=False, is_active=True).order_by('-id') or None
    else:
        tab = 'contractors'
        entries = ComplianceRecordEntry.objects.filter( is_deleted=False, is_active=True).order_by('-id') or None
    if user:
        return render(
            request,
            'compliance/staff_dashboard.html',
            {
                'title':'Compliance Report: Staff Dashboard',
                'year':datetime.now().year,
                'section':'staff',
                'tab':tab,
                'entries':entries,
                'records':records,
                'get_default_objects':get_default_objects(request)
            })
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#enable form
@login_required
def compliance_enable_form(request):
    if request.method == 'POST':
        if request.user.is_admin or request.user.is_staff:
            record = ComplianceRecord.objects.get(id=request.POST.get('record_id'))

            if record:
                if request.POST.get('submission_enabled'):
                    record.submission_enabled = True
                    messages.add_message(request, messages.SUCCESS, 'Forms have been enabled successfully. Contractors can now submit their reports')
                else:
                    record.submission_enabled = False
                    messages.add_message(request, messages.SUCCESS, 'Forms have been disabled successfully. Contractors are blocked from submitting reports')
                record.save()
               
                return redirect('staff_dashboard_tab', request.user.id, 'settings')
        
        messages.add_message(request, messages.ERROR, '(RequestMethodError): Data could not be submitted.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        messages.add_message(request, messages.ERROR, 'Something went wrong! Messages could not be sent. Please contact KoTDA ICT Office for assistance')
    return redirect('dashboard_view')
#############################################################################################################################################



#create inspection record in DB
@login_required
def create_inspection_record(request):
    if request.method == 'POST':
        if request.user.is_staff or request.user.is_admin:

            contractor = ContractorProfile.objects.get(id=request.POST.get("contractor_id"))
            module = ComplianceModule.objects.get(id=request.POST.get("module_id"))
            

            if contractor:

                inspection = Inspection()
                inspection.contractor = contractor;
                inspection.module = module
                inspection.created_by = request.user
                inspection.updated_by = request.user
            
                inspection.save()
                inspection.inspection_uid = str(contractor.company_name) +"/"+ str(GetFiscalYear()) + "/" + str(datetime.now().month) + "/" + str(datetime.now().day) + "/" + str(inspection.id)
                inspection.save()

                return redirect('get_inspection_form', inspection_id=inspection.id, tab="photo")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################

        


@login_required
def get_inspection_form(request, inspection_id, tab):
    if request.user.is_staff or request.user.is_admin:

        inspection = Inspection.objects.get(id=inspection_id)
        if inspection:

            contractor = ContractorProfile.objects.get(id=inspection.contractor.id)

            return render(
                request,
                'compliance/inspection/create_inspection.html',
                {
                    'title':'Compliance Report: Staff non-compliance Review',
                    'year':datetime.now().year,
                    'fdate':GetFiscalYear(),
                    'inspection' : inspection,
                    'tab':tab,
                    'get_default_objects':get_default_objects(request)
                })
    #default redirect
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



@login_required
def post_inspection(request):
    if request.user.is_staff or request.user.is_admin:
        if request.method == "POST":
            inspection = Inspection.objects.get(id=request.POST.get("inspection_id"))
            if inspection:
                inspection.observation = request.POST.get("observation")
                inspection.action = request.POST.get("action")
                inspection.coordinates = request.POST.get("coordinates")
                inspection.reference =ComplianceModuleReference.objects.get(id=request.POST.get("reference_id"))
                inspection.updated_by = request.user
                inspection.save()

                if 'save_photo' in request.POST:
                    inspection.status = 'DRAFT'
                    inspection.updated_by = request.user
                    inspection.save()
                    return redirect('get_inspection_form', inspection_id=inspection.id, tab="photo")
                elif 'save_video' in request.POST:
                    inspection.status = 'DRAFT'
                    inspection.updated_by = request.user
                    inspection.save()
                    return redirect('get_inspection_form', inspection_id=inspection.id, tab="video")
                elif 'save_document' in request.POST:
                    inspection.status = 'DRAFT'
                    inspection.updated_by = request.user
                    inspection.save()
                    return redirect('get_inspection_form', inspection_id=inspection.id, tab="document")

                

                elif 'save_draft' in request.POST:
                    #TODO: check who is submitting before submitting
                    inspection.status = 'DRAFT'
                    inspection.updated_by = request.user
                    inspection.save()
                    messages.add_message(request, messages.SUCCESS, 'Draft Inspection report saved successfully. Please confirm your information and submit when ready.')
                    return redirect('view_inspection_report', inspection_id = inspection.id)
                    

                elif 'delete_report' in request.POST:
                    inspection.status = 'DELETED'
                    inspection.is_deleted = True
                    inspection.updated_by = request.user
                    inspection.save()
                    return redirect('dashboard_view')

                

                return redirect('get_inspection_form', inspection_id=inspection.id, tab="photo")

            messages.add_message(request, messages.ERROR, '(RequestMethodError): Data could not be submitted.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    #default redirect
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#this is where the report actions take place | should have called this post_inspection_with_comments
@login_required
def post_inspection_comment(request):
    if request.user.is_staff or request.user.is_admin or request.user.is_projectmanager:
        if request.method == "POST":
            inspection = Inspection.objects.get(id=request.POST.get("inspection_id"))
            if inspection:
                
                #reject report(done by manager/team lead)
                if 'reject' in request.POST:
                    #check permission
                    if request.user.is_manager or request.user.is_teamlead:
                        
                        inspection.status = 'REJECTED'
                        inspection.is_rejected = True
                        inspection.is_published = False
                        inspection.is_resolved = False
                        inspection.rejected_at = datetime.now()
                        inspection.last_updated_by = request.user
                        inspection.evaluated_by = request.user
                        inspection.rejected_by = request.user
                        inspection.save()

                        #create comment instance
                        comment = InspectionComments()
                        comment.inspection = inspection
                        #get team lead comment
                        if request.POST.get("tl_comment"):
                            comment.comment = request.POST.get("tl_comment")
                            comment.is_reviewer_comment = False
                            comment.is_teamleader_comment = True
                            comment.is_manager_comment = False
                            comment.is_contractor_comment = False
                            comment.comment_type = 'TEAM_LEADER'
                            comment.comment_by = request.user
                            comment.save()


                            #send notification
                            #notify manager and other staff
                            try:
                                #send email
                                message = "The Non-Compliance report on "+ str(inspection.contractor) + ": ID NUMBER [ "+str(inspection.inspection_uid) +" ] has been rejected."
                                subject="Non-Compliance Report Rejected"
                                
                                

                                msg_html = render_to_string('compliance/emails/non_compliance_report.html',
                                                            {'subject': subject,
                                                            'message':message,
                                                            'contractor':inspection.contractor.project_manager,
                                                            'inspection':inspection,
                                                            })
          
                                send_mail(
                                    subject,
                                    msg_html,
                                    settings.EMAIL_HOST_USER,
                                    [request.user.email,inspection.created_by.email ],
                                    html_message=msg_html,
                                    fail_silently=False,
                                )

                            except:
                                pass

                        #get manager comment
                        if request.POST.get("mgmt_comment"):
                            comment.comment = request.POST.get("mgmt_comment")
                            comment.is_reviewer_comment = False
                            comment.is_teamleader_comment = False
                            comment.is_manager_comment = True
                            comment.is_contractor_comment = False
                            comment.comment_type = 'MANAGER'
                            comment.comment_by = request.user
                            comment.save()

                            #send notification
                            #notify manager and other staff
                            try:
                                #send email
                                message = "The Non-Compliance report on "+ str(inspection.contractor) + ": ID NUMBER [ "+str(inspection.inspection_uid) +" ] has been rejected."
                                subject="Non-Compliance Report Rejected"
                                
                                

                                msg_html = render_to_string('compliance/emails/non_compliance_report.html',
                                                            {'subject': subject,
                                                            'message':message,
                                                            'contractor':inspection.contractor.project_manager,
                                                            'inspection':inspection,
                                                            })
          
                                send_mail(
                                    subject,
                                    msg_html,
                                    settings.EMAIL_HOST_USER,
                                    [request.user.email,inspection.created_by.email ],
                                    html_message=msg_html,
                                    fail_silently=False,
                                )

                            except:
                                pass

                        messages.add_message(request, messages.SUCCESS, 'Inspection report rejected successfully')
                        return redirect('view_inspection_report', inspection_id=inspection.id)
                    else:
                        messages.add_message(request, messages.ERROR, '(PermissionError): Staff could not be updated successfully. You do not have enough priviledges.')
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                #reviewer forwards report to team leader
                if 'forward_tl' in request.POST:
                    if request.user.is_reviewer or request.user.is_admin:
                        inspection.status = 'PENDING_TEAM_LEADER_REVIEW'
                        inspection.is_rejected = False
                        inspection.is_published = False
                        inspection.is_resolved = False
                        inspection.last_updated_by = request.user
                        inspection.submitted_by = request.user
                        inspection.submitted_at = datetime.now()
                        inspection.save()

                        #create comment record
                        if request.POST.get("reviewer_comment"):
                            comment = InspectionComments()
                            comment.inspection = inspection
                            comment.comment = request.POST.get("reviewer_comment")
                            comment.is_reviewer_comment = True
                            comment.is_teamleader_comment = False
                            comment.is_manager_comment = False
                            comment.is_contractor_comment = False
                            comment.comment_type = 'MEMBER'
                            comment.comment_by = request.user
                            comment.save()

                            #notify manager and other staff
                            try:
                                #send email
                                message = "The Non-Compliance report on "+ str(inspection.contractor) + ": ID NUMBER [ "+str(inspection.inspection_uid) +" ] has been forwarded to the team leader successfully. Please wait for feedback."
                                subject="Non-Compliance Report Forwarded to Team Leader"
                                teamleaders = []
                                get_leaders = User.objects.filter(is_deleted=False,is_active=True,is_staff=True,is_teamlead=True).values('email') or None
                                
                                #collect teamleader emails
                                if get_leaders is not None:
                                    for leader in get_leaders:
                                        teamleaders.append(leader.email)
                                else:
                                    pass
                                

                                msg_html = render_to_string('compliance/emails/non_compliance_report.html',
                                                            {'subject': subject,
                                                            'message':message,
                                                            'contractor':inspection.contractor.project_manager,
                                                            'inspection':inspection,
                                                            })
          
                                send_mail(
                                    subject,
                                    msg_html,
                                    settings.EMAIL_HOST_USER,
                                    [request.user.email,get_leaders,'ppd-c@konza.go.ke' ],
                                    html_message=msg_html,
                                    fail_silently=False,
                                )

                            except:
                                pass

                            messages.add_message(request, messages.SUCCESS, 'Report forwarded to team leader successfully. Please wait for feedback.')
                            return redirect('view_inspection_report', inspection_id = inspection.id)
                    else:
                            messages.add_message(request, messages.ERROR, '(PermissionError): Report could not be updated successfully. You do not have correct priviledges. Please contact ICT office for assistance.')
                            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                
                #from team lead to manager
                if 'forward_cm' in request.POST:
                    if request.user.is_teamlead or request.user.is_admin:
                        inspection.status = 'PENDING_MANAGER_REVIEW'
                        inspection.last_updated_by = request.user
                        inspection.evaluated_by = request.user
                        inspection.evaluated_at = datetime.now()
                        inspection.save()

                        if request.POST.get("tl_comment"):
                            comment = InspectionComments()
                            comment.inspection = inspection
                            comment.comment = request.POST.get("tl_comment")
                            comment.is_reviewer_comment = False
                            comment.is_teamleader_comment = True
                            comment.is_manager_comment = False
                            comment.is_contractor_comment = False
                            comment.comment_type = 'TEAM_LEADER'
                            comment.comment_by = request.user
                            comment.save()

                            
                            #notify manager and other staff
                            try:
                                #send email
                                message = "The Non-Compliance report on "+ str(inspection.contractor) + " has been forwarded to the manager successfully. Please wait for feedback."
                                subject="Non-Compliance Report Forwarded to Manager"
                                managers = []
                                get_managers = User.objects.filter(is_deleted=False,is_active=True,is_staff=True,is_manager=True) or None
                                if get_managers is not None:
                                    for manager in get_managers:
                                        managers.append(manager.email)
                                else:
                                    pass
                                send_email_task.delay(
                                to=request.user.email,
                                subject=subject,
                                message=message)

              

                                msg_html = render_to_string('compliance/emails/submission_reminder.html',
                                                            {'subject': subject,
                                                            'message':message,
                                                            'contractor':inspection.contractor.project_manager
                                                            })
          
                                send_mail(
                                    subject,
                                    msg_html,
                                    settings.EMAIL_HOST_USER,
                                    [request.user.email,managers,'ppd-c@konza.go.ke' ],
                                    html_message=msg_html,
                                    fail_silently=False,
                                )

                            except:
                                pass

                            messages.add_message(request, messages.SUCCESS, 'Report forwarded to the manager successfully. Please wait for feedback.')
                            return redirect('view_inspection_report', inspection_id = inspection.id)
                            

                    else:
                        messages.add_message(request, messages.ERROR, '(PermissionError): Report failed to update. You do not have enough priviledges.')
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    
                    #publish: from manager to contractor
                if 'publish' in request.POST:
                    if request.user.is_manager or request.user.is_admin:
                        inspection.status = 'PUBLISHED'
                        inspection.last_updated_by = request.user
                        inspection.is_published = True
                        inspection.is_rejected = False
                        inspection.published_by = request.user
                        inspection.submitted_at = datetime.now()
                        inspection.save()

                        #get manager comment
                        if request.POST.get("mgmt_comment"):
                            comment = InspectionComments()
                            comment.inspection = inspection
                            comment.comment = request.POST.get("mgmt_comment")
                            comment.is_reviewer_comment = False
                            comment.is_teamleader_comment = False
                            comment.is_manager_comment = True
                            comment.is_contractor_comment = False
                            comment.comment_type = 'MANAGER'
                            comment.comment_by = request.user
                            comment.save()

                            #notify manager and other staff
                            try:
                                #send email
                                message = "The Non-Compliance report on "+ str(inspection.contractor) +" [ "+str(inspection.inspection_uid) +" ] has been published."
                                subject="Non-Compliance Report Published"
                                
                                get_contractor = User.objects.get(id=inspection.contractor.project_manager.id) or None
                                if get_contractor is not None:
                                    
                                    msg_html = render_to_string('compliance/emails/submission_reminder.html',
                                                                {'subject': subject,
                                                                'message':message,
                                                                'contractor':inspection.contractor.project_manager
                                                                })
          
                                    send_mail(
                                        subject,
                                        msg_html,
                                        settings.EMAIL_HOST_USER,
                                        [request.user.email,get_contractor.email,'ppd-c@konza.go.ke' ],
                                        html_message=msg_html,
                                        fail_silently=False,
                                    )
                                else:
                                    pass
                                send_email_task.delay(
                                to=request.user.email,
                                subject=subject,
                                message=message)

          

                            except:
                                pass

                            messages.add_message(request, messages.SUCCESS, 'Report published successfully. Contractor has been notified')
                            return redirect('view_inspection_report', inspection_id = inspection.id)
                            

                    else:
                        messages.add_message(request, messages.ERROR, '(PermissionError): Report failed to publish. You do not have enough priviledges.')
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


                  #contractor response
                if 'contractor_response' in request.POST:
                    if request.user.is_projectmanager or request.user.is_admin:
                        
                        #get project manager comment
                        if request.POST.get("pm_comment"):
                            comment = InspectionComments()
                            comment.inspection = inspection
                            comment.comment = request.POST.get("pm_comment")
                            comment.is_reviewer_comment = False
                            comment.is_teamleader_comment = False
                            comment.is_manager_comment = False
                            comment.is_contractor_comment = True
                            comment.comment_type = 'CONTRACTOR'
                            comment.comment_by = request.user
                            comment.save()

                            #notify manager and other staff
                            try:
                                #send email
                                message = "Your comments on the non compliance report- "+ str(inspection.contractor) +" [ "+str(inspection.inspection_uid) +" ] have been sent to PPDC."
                                subject="Non-Compliance Comments sent to PPDC"
                                
                                staffs = []
                                get_staff = User.objects.filter(is_deleted=False,is_active=True,is_staff=True) or None
                                if get_staff is not None:
                                    for staff in get_staff:
                                        staffs.append(staff.email)
                                else:
                                    pass
                                
                                
                                if get_staff is not None:
                                    
                                    msg_html = render_to_string('compliance/emails/submission_reminder.html',
                                                                {'subject': subject,
                                                                'message':message,
                                                                'contractor':inspection.contractor.project_manager
                                                                })
          
                                    send_mail(
                                        subject,
                                        msg_html,
                                        settings.EMAIL_HOST_USER,
                                        [request.user.email,staffs,'ppd-c@konza.go.ke' ],
                                        html_message=msg_html,
                                        fail_silently=False,
                                    )
                                else:
                                    pass
                                send_email_task.delay(
                                to=request.user.email,
                                subject=subject,
                                message=message)

          

                            except:
                                pass

                            messages.add_message(request, messages.SUCCESS, 'Your comments have been sent to PPDC successfully.')
                            return redirect('view_inspection_report', inspection_id = inspection.id)
                            

                    else:
                        messages.add_message(request, messages.ERROR, '(PermissionError): Comments failed to submit. You do not have enough priviledges.')
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                    


                
                    messages.add_message(request, messages.SUCCESS, 'Inspection report has been forwarded to the manager successfully')
                    return redirect('view_inspection_report', inspection_id=inspection.id)
                    #end send contractor reply


                    #TODO::I'm sending a lot of shit to this function, we may have to refactor really well from here
                if 'save_submit' in request.POST:
                    #TODO: check who is submitting before submitting
                    inspection.status = 'PENDING_TEAM_LEADER_REVIEW'
                    inspection.updated_by = request.user
                    inspection.save()

                    #send notifications

                    return redirect('view_inspection_report', inspection_id = inspection.id)
                    messages.add_message(request, messages.SUCCESS, 'Inspection report saved successfully')


                elif 'save_draft' in request.POST:
                    #TODO: check who is submitting before submitting
                    inspection.status = 'DRAFT'
                    inspection.updated_by = request.user
                    inspection.save()
                    return redirect('view_inspection_report', inspection_id = inspection.id)
                    messages.add_message(request, messages.SUCCESS, 'Draft Inspection report saved successfully. Please submit when ready.')

                elif 'delete_report' in request.POST:
                    inspection.status = 'DELETED'
                    inspection.is_deleted = True
                    inspection.updated_by = request.user
                    inspection.save()
                    return redirect('dashboard_view')

                

                return redirect('get_inspection_form', inspection_id=inspection.id, tab="photo")

            messages.add_message(request, messages.ERROR, '(InspectionGetNullException): Data could not be submitted. Inspection record list empty')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        messages.add_message(request, messages.ERROR, 'Comment submit Failed. You do not have permission to delete this comment.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################




#not used at the momment. words once said can not be unsaid
@login_required
def delete_inspection_comment(request, comment_id):
    comment = InspectionComments.objects.get(id=comment_id)
    #security check
    if request.user == comment.comment_by or request.user.is_admin:
        comment.is_deleted = True
        comment.save()
        messages.add_message(request, messages.SUCCESS, 'Comment deleted successfully')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    messages.add_message(request, messages.ERROR, 'Comment delete Failed. You do not have permission to delete this comment.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



@login_required
def reviewer_profile(request, reviewer_id, tab=None):
    reviews = Inspection.objects.filter(created_by=request.user,is_deleted=False).order_by('-id')
    reviewer = User.objects.get(id=reviewer_id) or None
    if reviewer != None:
        return render(
                request,
                'compliance/inspection/view_staff_profile.html',
                {
                    'title':'Non Compliance |'+ str(reviewer.last_name) +' Reviewer profile',
                    'message':'Manage your reports',
                    'year':datetime.now().year,
                    'tab':tab,
                    'reviews':reviews,
                    'reviewer':reviewer,
                    'get_default_objects':get_default_objects(request)
                }
    
            )

    #default redirect
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################
            


@login_required
def view_inspection_report(request, inspection_id):
    inspection = Inspection.objects.get(id=inspection_id,is_deleted=False)
    reviewee = User.objects.get(id=inspection.contractor.project_manager.id) or None
    if inspection != None:
        if request.user.is_staff or request.user.is_admin or request.user == reviewee:
            return render(
                request,
                'compliance/inspection/view_inspection_report.html',
                {
                    'title':'Non Compliance |'+ str(inspection.created_by) +'s Report',
                    'message':'View your report',
                    'year':datetime.now().year,
                    'inspection':inspection,
                    'get_default_objects':get_default_objects(request)
                }
    
            )
    #default redirect
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################


@login_required
def delete_inspection_photo(request, photo_id):
    photo = InspectionPhotoEvidence.objects.get(id=photo_id)

    if request.user == photo.uploaded_by or request.user.is_admin:
        photo.is_deleted = True
        photo.save()
        messages.add_message(request, messages.SUCCESS, 'Photo deleted successfully')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    messages.add_message(request, messages.ERROR, 'Photo delete Failed. you do not have enough priviledges.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



@login_required
def delete_inspection_document(request, document_id):
    document = InspectionDocumentEvidence.objects.get(id=document_id)

    if request.user == document.uploaded_by or request.user.is_admin:
        document.is_deleted = True
        document.save()
        messages.add_message(request, messages.SUCCESS, 'Document deleted successfully')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    messages.add_message(request, messages.ERROR, 'Document delete Failed. you do not have enough priviledges.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################




@login_required
def toggle_noncompliance_resolve_status(request):
    if request.method == 'POST':
        inspection = Inspection.objects.get(id=request.POST.get('inspection_id'))
        #check if its the right guy appointing
        if request.user.is_manager or request.user.is_teamlead or request.user.is_admin or request.user == inspection.created_by:
            
            if request.POST.get('is_resolved'):
                inspection.is_resolved = True
                inspection.status = 'COMPLIED'
            elif not request.POST.get('is_resolved'):
                inspection.is_resolved = False
                inspection.status = 'PUBLISHED'
            inspection.last_updated_by = request.user
            inspection.save()

            messages.add_message(request, messages.SUCCESS, 'Report updated successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.add_message(request, messages.ERROR, '(PermissionError): Report could not be updated successfully. You do not have enough priviledges.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    #default redirect
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################


#download report page
@login_required
def inspection_report_download(request, inspection_id):
    inspection = Inspection.objects.get(id=inspection_id,is_deleted=False)
    if inspection != None:
        if request.user.is_staff or request.user.is_admin or request.user == inspection.created_by or request.user == inspection.contractor.project_manager:
               
            template = Template('compliance/inspection_report_download.html')
            context = Context({
                "inspection": inspection,
            })
            html = template.render(context)
            pdf = render_to_pdf('compliance/inspection_report_download.html', {"inspection": inspection,})
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "Report_%s.pdf" %(str(inspection.inspection_uid)+"_"+str(inspection.status))
                content = "inline; filename=%s" %(filename)
                download = request.GET.get("download")
                if download:
                    content = "attachment; filename=%s" %(filename)
                response['Content-Disposition'] = content
                return response
            return HttpResponse("Not found")

        messages.add_message(request, messages.ERROR, 'Download Failed. Access Denied. Contact ICT for assistance.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################


@login_required
def delete_inspection_video(request, video_id):
    video = InspectionVideoEvidence.objects.get(id=video_id)

    if request.user == video.uploaded_by or request.user.is_admin:
        video.is_deleted = True
        video.save()
        messages.add_message(request, messages.SUCCESS, 'Video deleted successfully')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    messages.add_message(request, messages.ERROR, 'Video delete Failed. you do not have enough priviledges')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



@login_required
def create_staff_account(request):
    if request.method == "POST":
        if request.user.is_manager or request.user.is_teamlead or  request.user.is_admin:
            user = User()

            try:
                #update db
                if request.POST.get('username'):
                    user.username = request.POST.get('username')

                if request.POST.get('email'):
                    user.email = request.POST.get('email')

                if request.POST.get('first_name'):
                    user.first_name = request.POST.get('first_name')

                if request.POST.get('last_name'):
                    user.last_name = request.POST.get('last_name')

                if request.FILES.get('avatar'):
                    user.avatar = request.FILES.get('avatar')

                if request.POST.get('bio'):
                    user.bio = request.POST.get('bio')

                if request.POST.get('is_teamlead'):
                    user.is_teamlead = True

                #create and set password
                password = "KOTDACompliance1010"
                user.set_password(password)

                user.is_staff = True
                user.is_reviewer = True
                user.save()

                subject = "Staff account created successfully"
                message = "Staff account for "+str(user.last_name)+" has been created successfully. Login credentials email-"+ str(user.email)+ ". Your password is- "+str(password)+". Change your password after login."
                msg_html = render_to_string('compliance/emails/submission_reminder.html',
                                                                {'subject': subject,
                                                                'message':message,
                                                                'contractor':user,
                                                                })
          
                send_mail(
                    subject,
                    msg_html,
                    settings.EMAIL_HOST_USER,
                    [user.email, request.user.email ],
                    html_message=msg_html,
                    fail_silently=False,
                )

            except Exception as e:
                messages.add_message(request, messages.ERROR, '(POSTError): Report could not be updated successfully.' + str(e))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            messages.add_message(request, messages.SUCCESS, 'New staff created successfully')
            return redirect('dashboard_tab_view', tab='settings')
        else:
            messages.add_message(request, messages.ERROR, '(PermissionError): Report could not be updated successfully. You do not have enough priviledges.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    #default redirect
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#create contractor user account
@login_required
def create_contractor_account(request):
    if request.method == "POST":
        if request.user.is_manager or request.user.is_teamlead or request.user.is_admin:
            user = User()

            try:
                #update db
                if request.POST.get('username'):
                    user.username = request.POST.get('username')

                if request.POST.get('email'):
                    user.email = request.POST.get('email')

                if request.POST.get('first_name'):
                    user.first_name = request.POST.get('first_name')

                if request.POST.get('last_name'):
                    user.last_name = request.POST.get('last_name')

                if request.FILES.get('avatar'):
                    user.avatar = request.FILES.get('avatar')

                if request.POST.get('bio'):
                    user.bio = request.POST.get('bio')

                

                password = "KOTDACompliance1010"
                user.set_password(password)

                user.is_projectmanager = True
                user.save()

                profile = ContractorProfile()
                if request.POST.get('company_name'):
                    profile.company_name = request.POST.get('company_name')
                profile.project_manager = user
                profile.is_active = True
                profile.save()

                subject = "Contractor account created successfully"
                message = "Contractor account for "+str(user.last_name)+" has been created successfully. Login credentials "+ str(user.email)+ ". Your password is "+str(password)+". Change your password after login."
                msg_html = render_to_string('compliance/emails/submission_reminder.html',
                                                                {'subject': subject,
                                                                'message':message,
                                                                'contractor':user,
                                                                })
          
                send_mail(
                    subject,
                    msg_html,
                    settings.EMAIL_HOST_USER,
                    [user.email, request.user.email ],
                    html_message=msg_html,
                    fail_silently=False,
                )

            except Exception as e:
                messages.add_message(request, messages.ERROR, '(POSTError): Account could not be created.' + str(e))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            messages.add_message(request, messages.SUCCESS, 'New contractor created successfully')
            return redirect('staff_dashboard_section_toggle', section='contractor', tab='contractors')
        else:
            messages.add_message(request, messages.ERROR, '(PermissionError): Contractor create fail. You do not have enough priviledges.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    #default redirect
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#block contractor from submitting monthly report
@login_required
def block_contractor(request):
    if request.method == "POST":
        if request.user.is_manager or request.user.is_admin:
            contractor = ContractorProfile.objects.get(id=request.POST.get('contractor_id'))

            try:
                #update db
                if request.POST.get('is_acknowledged'):
                    contractor.is_blocked = True
                    contractor.blocked_by = request.user
                    contractor.blocked_at = datetime.now()

                if request.POST.get('block_reason'):
                    contractor.block_reason = request.POST.get('block_reason')

                contractor.save()

                subject = "Contractor account blocked"
                message = "Contractor account for "+str(contractor.company_name)+" has been blocked. The account will no longer be able to submit monthly reports."
                msg_html = render_to_string('compliance/emails/submission_reminder.html',
                                                                {'subject': subject,
                                                                'message':message,
                                                                'contractor':contractor.project_manager,
                                                                })
          
                send_mail(
                    subject,
                    msg_html,
                    settings.EMAIL_HOST_USER,
                    [contractor.project_manager.email, request.user.email, 'ppd-c@konza.go.ke' ],
                    html_message=msg_html,
                    fail_silently=False,
                )

            except Exception as e:
                messages.add_message(request, messages.ERROR, '(POSTError): Account could not be blocked.' + str(e))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            messages.add_message(request, messages.SUCCESS, 'Contractor account blocked successfully')
            return redirect('staff_dashboard_section_toggle', section='contractor', tab='contractors')
        else:
            messages.add_message(request, messages.ERROR, '(PermissionError): Contractor block fail. You do not have enough priviledges.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    #default redirect
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



@login_required
def unblock_contractor(request):
    if request.method == "POST":
        if request.user.is_manager or request.user.is_admin:
            contractor = ContractorProfile.objects.get(id=request.POST.get('contractor_id'))

            try:
                #update db
                if request.POST.get('is_acknowledged'):
                    contractor.is_blocked = False

                if request.POST.get('block_reason'):
                    contractor.block_reason = request.POST.get('block_reason')

                contractor.save()

                subject = "Contractor account unblocked"
                message = "Contractor account for "+str(contractor.company_name)+" has been unblocked. The account is now able to submit monthly reports."
                msg_html = render_to_string('compliance/emails/submission_reminder.html',
                                                                {'subject': subject,
                                                                'message':message,
                                                                'contractor':contractor.project_manager,
                                                                })
          
                send_mail(
                    subject,
                    msg_html,
                    settings.EMAIL_HOST_USER,
                    [contractor.project_manager.email, request.user.email, 'ppd-c@konza.go.ke' ],
                    html_message=msg_html,
                    fail_silently=False,
                )

            except Exception as e:
                messages.add_message(request, messages.ERROR, '(POSTError): Account could not be unblocked.' + str(e))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            messages.add_message(request, messages.SUCCESS, 'Contractor account unblocked successfully')
            return redirect('staff_dashboard_section_toggle', section='contractor', tab='contractors')
        else:
            messages.add_message(request, messages.ERROR, '(PermissionError): Contractor unblock fail. You do not have enough priviledges.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    #default redirect
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################


#read requirement attachment upload
@login_required
def read_requirement_attachment(request,document_id):
    document = ComplianceRequirementAttachmentSubmission.objects.get(id=document_id)
    if document.record_entry.created_by == request.user or request.user.is_staff or request.user.is_admin:
        
        return render(
            request,
            'compliance/view_document.html',
            {
                'title':'Non Compliance |'+ str(document.attachment.name) +' (read)',
                'message':'View your document',
                'year':datetime.now().year,
                'document':document,
                'get_default_objects':get_default_objects(request)
            }
        )
    else:
        messages.add_message(request, messages.ERROR, '(ACCESS_DENIED):Document could not be opened. You do not have enough priviledges.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#############################################################################################################################################



#remind contractors to submit reports
@login_required
def send_reminder_message(request):
    if request.method == 'POST':
        if datetime.now().month-1 == 0:
            month = 12
            year = datetime.now().year-1
        else:
            month = datetime.now().month
            year = datetime.now().year
        

        if request.POST.get('subject') and request.POST.get('message') and request.user.is_staff:
            
            try:

                subject = request.POST.get('subject')
                message = request.POST.get('message')
                #get contractors who have not created an entry
                unreported_contractors = User.objects.filter(is_projectmanager=True, is_active=True)
                if unreported_contractors.count() <= 0:
                    messages.add_message(request, messages.INFO, 'All contractors have submitted reports')
                    return redirect('dashboard_view')
                 #get entries
                entries = ComplianceRecordEntry.objects.filter(month=month,year=year,is_active=True).values('last_updated_by')
            
                #get contractors who have created entry but not submitted
                for contractor in unreported_contractors:
                    if contractor not in entries:
                        #send reminder to submit report
                        #logger.info(f"from={EMAIL_HOST_USER}, {to=}, {subject=}, {message=}")
                    
                            #logger.info("About to send_mail")
                            #send_mail(subject, message, EMAIL_HOST_USER, [to])
                        #   send_mail(
                        #           subject,
                        #           message,
                        #           EMAIL_HOST_USER,
                        #           [contractor.email],
                        #           fail_silently=False,
                        #       )
                    
                            #send email
                        msg_html = render_to_string('compliance/emails/submission_reminder.html',
                                                    {'subject': subject,
                                                    'message':message,
                                                    'contractor':contractor
                                                    })
          
                        send_mail(
                            subject,
                            msg_html,
                            settings.EMAIL_HOST_USER,
                            [contractor.email],
                            html_message=msg_html,
                            fail_silently=False,
                        )

                        messages.add_message(request, messages.SUCCESS, 'Messages sent successfully')
                        return redirect('dashboard_view')
            except:
                messages.add_message(request, messages.ERROR, '(POST.AccessError)! Messages could not be sent. Please contact KoTDA ICT Office for assistance')
                return redirect('dashboard_view')

                
        else:
            messages.add_message(request, messages.ERROR, '(POST.AccessError)! Messages could not be sent. Please contact KoTDA ICT Office for assistance')
            return redirect('dashboard_view')
                

    messages.add_message(request, messages.ERROR, 'Something went wrong! Messages could not be sent. Please contact KoTDA ICT Office for assistance')
    return redirect('dashboard_view')                            
#############################################################################################################################################



#seed form information
@login_required
def seed_compliance_form(request):
    #seeds the database with department data##
    compliance_form_path = path.join(path.dirname(__file__), 'compliance_form.json')
    with open(compliance_form_path, 'r') as compliance_form_file:
        samples_form = json.load(compliance_form_file)

    for sample_form in samples_form:
        record = ComplianceRecord()
        record.organization_name = sample_form['organization_name']
        record.notes = sample_form['notes']
        record.type = sample_form['type']
        record.is_active = sample_form['is_active']
        record.save()

        for sample_designation in sample_form['personnel_designation']:
            designation = PersonnelDesignation()
            designation.record = record
            designation.designation_name = sample_designation['designation_name']
            if sample_designation['type'] == 1:
                designation.type = 'CONSTRUCTION SUPERVISING CONSULTANT’S PROFFESSIONALS'
            elif sample_designation['type'] == 2:
                designation.type = "CONSTRUCTION CONTRACTOR’S PERSONNEL"
            designation.save()
        
        for sample_module in sample_form['module']:
            module = ComplianceModule()
            module.compliance_record = record
            module.name = sample_module['name']
            module.type = sample_module['type']
            module.notes = sample_module['notes']
            module.save()

            for sample_reference in sample_module['reference']:
                reference = ComplianceModuleReference()
                reference.module = module
                reference.reference = sample_reference['reference']
                reference.parameter = sample_reference['parameter']
                reference.notes = sample_reference['notes']
                reference.save()

                for sample_requirement in sample_reference['requirements']:
                    requirement = ComplianceReferenceRequirement()
                    requirement.reference = reference
                    requirement.requirement_name = sample_requirement['requirement_name']
                    requirement.notes = sample_requirement['notes']
                    requirement.save()

                    for sample_attachment in sample_requirement['attachments']:
                        attachment = ComplianceRequirementAttachmentDetails()
                        attachment.requirement = requirement
                        attachment.document_name = sample_attachment['document_name']
                        attachment.notes = sample_attachment['notes']
                        attachment.save()

                    for sample_metric in sample_requirement['metrics']:
                        metric = ComplianceRequirementMetric()
                        metric.requirement = requirement
                        metric.metric_type = sample_metric['metric_type']
                        metric.input_type = sample_metric['input_type']
                        metric.is_required = sample_metric['is_required']
                        metric.notes = sample_metric['notes']
                        metric.save()


    messages.add_message(request, messages.SUCCESS, 'Compliance forms created successfully')

   # return HttpResponseRedirect(reverse('app:home'))
    return redirect('home')
#############################################################################################################################################


#seed entries
@login_required
def seed_entries(request,record_id,count):
    record = ComplianceRecord.objects.get(id=record_id)

    if request.user.is_contractor or request.user.is_projectmanager: 
        #seeds the database with entry data##
        entry_path = path.join(path.dirname(__file__), 'compliance_entries.json')
        with open(entry_path, 'r') as entry_file:
            entries = json.load(entry_file)

        for counter in enumerate([1, 2, 3, 4, 5, 6, 7]):
            new_entry = ComplianceRecordEntry()
            new_entry.compliance_record = record
            new_entry.project_name = entries['project_name'] + str(random.randrange(100,300)) + str(datetime.now().second)
            new_entry.summary = entries['summary']
            new_entry.month = random.randrange(1,12)
            new_entry.year = random.randrange(2000,2019)
            new_entry.created_by = request.user
            new_entry.last_updated_by = request.user
            new_entry.save()

            #create personnel instance
            personnel_designations = PersonnelDesignation.objects.filter(record=record)
            for designation in personnel_designations:
                for person in entries['personnel']:
                    personnel = Personnel()
                    personnel.record_entry = new_entry
                    personnel.first_name = person['first_name']
                    personnel.other_name = person['other_name']
                    personnel.email = person['email']
                    personnel.tel_number = person['tel_number']
                    personnel.last_updated_by = request.user
                    personnel.designation = designation
                    personnel.save()

             ###create instances of modules
            modules = ComplianceModule.objects.filter(compliance_record=record)
            
            #create metrics instance
            for module in modules:
                references =  ComplianceModuleReference.objects.filter(module=module)
                for reference in references:
                    requirements = ComplianceReferenceRequirement.objects.filter(reference=reference)
                    for requirement in requirements:
                        metrics = ComplianceRequirementMetric.objects.filter(requirement=requirement)
                        for metric in metrics:
                            for metric_notes in entries['metric_submission']:
                                #create empty metric submissions
                                submission = ComplianceRequirementMetricSubmission()
                                submission.metric = metric
                                if metric.input_type == 'text':
                                    submission.notes = metric_notes['notes']
                                elif metric.input_type == 'int':
                                    submission.notes = random.randrange(1,200)
                                submission.last_updated_by = request.user
                                submission.record_entry = new_entry
                                submission.save()

                

                #TODO:success notification
            messages.add_message(request, messages.INFO, 'Forms populated successfully.(For Testing)')
            return redirect('home')
      
    messages.add_message(request, messages.ERROR, 'Forms could not be polulated. Kuna shida pahali')
    return redirect('home')
#############################################################################################################################################
