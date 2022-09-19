"""
Definition of urls for ComplianceReporting.
"""

from datetime import datetime
from django.urls import path, reverse
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from user_auth import views as user_views
from app import forms, views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls import url, include

#Sentry route error trigger

def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    #admin urls from django
    path('admin/', admin.site.urls),
    #general home url for all users
    path('dashboard/', views.dashboard_view, name='home'),
    path('dashboard/<str:tab>', views.dashboard_tab_view, name='dashboard_tab_view'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('report/download/<int:entry_id>/', views.report_download, name='report_download'),

    #download inspection report summary
    path('report/download/inspection/<int:inspection_id>/', views.inspection_report_download, name='inspection_report_download'),
    
    # user login/logout, pasword reset views
    path('login/', auth_views.LoginView.as_view(template_name='user_auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='user_auth/logout.html'), name='logout'),
    path('profile/', user_views.profile, name='profile'),
    #view staff dashboard
    path('dashboard/staff/<int:user_id>', views.staff_dashboard, name='staff_dashboard'),
    #view staff dashboard section
    path('dashboard/ppdc/get_section/<str:section>/<str:tab>', views.staff_dashboard_section_toggle, name='staff_dashboard_section_toggle'),
    #filter dashboard by tab
    path('dashboard/staff/<int:user_id>/<str:tab>', views.staff_dashboard_tab, name='staff_dashboard_tab'),
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='user_auth/password_reset.html'
            ), 
        name='password_reset'),
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='user_auth/password_reset_done.html'
            ), 
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='user_auth/password_reset_confirm.html'
            ), 
        name='password_reset_confirm'),
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='user_auth/password_reset_complete.html'
            ), 
        name='password_reset_complete'),
    path('', include('compliance.urls')),

    #seed forms labels
    path('seed/compliance_form/construction/', views.seed_compliance_form, name='seed_compliance_form'),
    #seed forms data. jaza form
    path('seed/compliance_data/construction/<int:record_id>/<int:count>/', views.seed_entries, name='seed_entries'),
    
    #home | dashboard
    path('compliance/dashboard/', views.dashboard_view, name='dashboard_view'),
    #list draft reports
    path('compliance/report/list/<int:record_id>/draft/', views.list_draft_reports, name='list_draft_reports'),
     #list submitted reports
    path('compliance/report/list/<int:record_id>/submitted/', views.list_submitted_reports, name='list_submitted_reports'),
     #list submitted reports
    path('compliance/report/list/<int:record_id>/submitted/personal/', views.list_mysubmitted_reports, name='list_mysubmitted_reports'),
    #list acknowledged reports
    path('compliance/report/list/<int:record_id>/acknowledged/', views.list_acknowledged_reports, name='list_acknowledged_reports'),
    #list contractors
    path('compliance/contractor/list/', views.list_contactors, name='list_contactors'),
    #view contractor's profile
    path('compliance/contractor/<int:contractor_id>/<str:tab>', views.contractor_profile, name='contractor_profile'),
    
    path('compliance/entry/<int:record_id>/', views.compliance_entry_form, name='compliance_entry_form'),

    #enable submissions
    path('compliance/enable/form/', views.compliance_enable_form, name='compliance_enable_form'),
    #update contractor details
    path('contractor/update/', views.update_contractor_details, name='update_contractor_details'),
    #update staff details
    path('staff/update/', views.update_staff_details, name='update_staff_details'),
    #update user password
    path('contractor/update/password/', views.change_password, name='change_password'),

    #to personel report views
    path('compliance/report/entry/<int:entry_id>/personnel', views.view_entry_report, name='view_entry_report'),
    #to metrics report views
    path('compliance/report/entry/<int:entry_id>/module/<int:module_id>/', views.view_entry_module_report, name='view_entry_module_report'),

    #create entry 
    path('compliance/entry/create', views.create_compliance_entry, name='create_compliance_entry'),
     #create new entry from previous entry
    path('compliance/entry/inherit/create', views.create_entry_from_previous, name='create_entry_from_previous'),
    #update metric entry
    path('compliance/entry/update', views.update_compliance_entry, name='update_compliance_entry'),
    #update personnel entry
    path('compliance/entry/personnel/update', views.update_personnel_details, name='update_personnel_details'),
    #create extra personnel entry
    path('compliance/entry/personnel/create', views.create_extra_personnel, name='create_extra_personnel'),
    #delete entry
    path('compliance/entry/delete/<int:entry_id>/', views.delete_entry, name='delete_entry'),
    #acknowledge entry
    path('compliance/entry/acknowledge/', views.acknowledge_entry, name='acknowledge_entry'),
    #submit entry
    path('compliance/entry/submit/', views.submit_report_entry, name='submit_report_entry'),
     #raise non compliance issue
    path('non_compliance/issue/raise/', views.raise_noncompliance_issue, name='raise_noncompliance_issue'),
     #delete non compliance issue
    path('non_compliance/issue/delete/<int:issue_id>/', views.delete_noncompliance_issue, name='delete_noncompliance_issue'),
     #raise personnel non compliance issue
    path('non_compliance/personnel/issue/raise/', views.raise_personnel_noncompliance_issue, name='raise_personnel_noncompliance_issue'),
     #delete personnel non-compliance issue
    path('non_compliance/personnel/issue/delete/<int:issue_id>/', views.delete_personnel_noncompliance_issue, name='delete_personnel_noncompliance_issue'),
    
    #delete personnel attachment
    path('compliance/entry/personnel/attachment/delete/<int:document_id>/', views.delete_personnel_attachment, name='delete_personnel_attachment'),
    #delete metric attachment
    path('compliance/entry/requirement/attachment/delete/<int:document_id>/', views.delete_requirement_attachment, name='delete_requirement_attachment'),
    #read metric attachment
    path('compliance/entry/requirement/attachment/read/<int:document_id>/', views.read_requirement_attachment, name='read_requirement_attachment'),
    #download attachments
    path('compliance/entry/requirement/attachment/download/<int:document_id>/', views.download_requirement_attachment, name='download_requirement_attachment'),
    #get compliance form view template
    path('compliance/entry/<int:entry_id>/record/<int:record_id>/', views.compliance_form_view, name='compliance_form_view'),
    #when user clicks on a reference to reveal corresponding requirements
    path('compliance/entry/<int:entry_id>/record/<int:record_id>/reference/<int:reference_id>/', views.compliance_reference_select, name='compliance_reference_select'),
    #user clicks on personnel link to reveal designation list
    path('compliance/entry/<int:entry_id>/record/<int:record_id>/personnel/', views.compliance_personnel_select, name='compliance_personnel_select'),
    #user clicks on requirement to reveal form
    path('compliance/form/entry/<int:entry_id>/record/<int:record_id>/reference/<int:reference_id>/requirement/<int:requirement_id>/', views.compliance_requirement_view, name='compliance_requirement_view'),
    #user clicks on personnel designation to reveal personnel form
    path('compliance/form/entry/<int:entry_id>/record/<int:record_id>/personnel/<int:personnel_id>/', views.compliance_personnel_view, name='compliance_personnel_view'),
     #send reminder message 
    path('compliance/reminder/send', views.send_reminder_message, name='send_reminder_message'),
    
    #autocomplete 
  #create inpection entry 
    path('compliance/inspection/create', views.create_inspection_record, name='create_inspection_record'),

    #inspection form get
    path('compliance/inspection/<int:inspection_id>/<str:tab>/get', views.get_inspection_form, name='get_inspection_form'),

     #basic upload used for non compliance uploads
    url(r'^basic-upload/$', views.BasicUploadView.as_view(), name='basic_upload'),

    #create inspection entry 
    path('compliance/inspection/create/post', views.post_inspection, name='post_inspection'),
   
    #create inspection entry 
    path('compliance/inspection/comment/post', views.post_inspection_comment, name='post_inspection_comment'),
   
    #view reviewer's profile
    path('compliance/reviewer/<int:reviewer_id>/<str:tab>', views.reviewer_profile, name='reviewer_profile'),
    
   #view reviewer's report
    path('compliance/inspection/<int:inspection_id>/view/report', views.view_inspection_report, name='view_inspection_report'),
    
   #delete reviewer's photo eveidence
    path('compliance/inspection/<int:photo_id>/photo/delete', views.delete_inspection_photo, name='delete_inspection_photo'),
   
    #delete reviewer's document eveidence
    path('compliance/inspection/<int:document_id>/document/delete', views.delete_inspection_document, name='delete_inspection_document'),
   

    #delete reviewer's video evidence
    path('compliance/inspection/<int:video_id>/video/delete', views.delete_inspection_video, name='delete_inspection_video'),
     #delete comment
    path('compliance/inspection/<int:comment_id>/comment/delete', views.delete_inspection_comment, name='delete_inspection_comment'),
    
   #update user details
    path('compliance/staff/appoint_teamlead', views.appoint_teamlead, name='appoint_teamlead'),
    
    #toggle noncompliance resolution
    path('compliance/inspection/resolution', views.toggle_noncompliance_resolve_status, name='toggle_noncompliance_resolve_status'),
    
    #create staff record
    path('staff/create/', views.create_staff_account, name='create_staff_account'),

    #block contractor account
    path('contractor/block/', views.block_contractor, name='block_contractor'),

    #unblock contractor account
    path('contractor/unblock/', views.unblock_contractor, name='unblock_contractor'),

        #create contractor record
    path('contractor/create/', views.create_contractor_account, name='create_contractor_account'),
    
    #sentry path
    path('sentry-debug/', trigger_error),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
         urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "KoTDA | Compliance Admin"
admin.site.site_title = "KoTDA | Compliance Admin Portal"
admin.site.index_title = "KoTDA | Compliance Admin Portal"
