from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
from app.models import *
from django.apps import apps

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have a username.')

        user = self.model(
                email = self.normalize_email(email),
                username= username
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
                email = self.normalize_email(email),
                password = password,
                username= username
            )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user



class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    bio = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='avatarImages/',null=True,blank=True, default="https://resourcecenter.konza.go.ke/media/repoImages/Konza-Technopolis-logo.png")
    last_name = models.CharField(max_length=15, null=True, blank=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date-joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last-login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)#PPDC
    is_reviewer = models.BooleanField(default=False)#PPDC
    is_teamlead = models.BooleanField(default=False)#PPDC
    is_manager = models.BooleanField(default=False)#PPDC
    
    is_superuser = models.BooleanField(default=False)
    is_projectmanager = models.BooleanField(default=False)
    is_contractor = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def get_contractor_profile(self):
        model = apps.get_model('app', 'ContractorProfile')
        profile = model.objects.filter(project_manager=self, is_deleted=False)
        return profile

    def get_draft_reports(self):
        model = apps.get_model('app', 'ComplianceRecordEntry')
        entries = model.objects.filter(created_by=self,status='draft', is_deleted=False)
        return entries

    def get_pending_reports(self):
        model = apps.get_model('app', 'ComplianceRecordEntry')
        entries = model.objects.filter(created_by=self,status='pending', is_deleted=False)
        return entries


    def get_acknowledged_reports(self):
        model = apps.get_model('app', 'ComplianceRecordEntry')
        entries = model.objects.filter(created_by=self,is_published=True, is_deleted=False)
        return entries

    def get_rejected_reports(self):
        model = apps.get_model('app', 'ComplianceRecordEntry')
        entries = model.objects.filter(created_by=self,is_rejected=True, is_deleted=False)
        return entries

    #staff reviews(get reviewer records) start
    def get_all_reviews(self):
        model = apps.get_model('app', 'Inspection')
        reports = model.objects.filter(created_by=self, is_deleted=False).order_by('-id')
        return reports

    def get_draft_reviews(self):
        model = apps.get_model('app', 'Inspection')
        reports = model.objects.filter(created_by=self,status="DRAFT", is_deleted=False).order_by('-id')
        return reports

    def get_pending_teamlead_reviews(self):
        model = apps.get_model('app', 'Inspection')
        reports = model.objects.filter(created_by=self,status="PENDING_TEAM_LEADER_REVIEW", is_deleted=False).order_by('-id')
        return reports

    def get_pending_manager_reviews(self):
        model = apps.get_model('app', 'Inspection')
        reports = model.objects.filter(created_by=self,status="PENDING_MANAGER_REVIEW", is_deleted=False).order_by('-id')
        return reports

    def get_total_pending_reviews(self):
        model = apps.get_model('app', 'Inspection')
        report_total = []
        reports_1 = model.objects.filter(created_by=self,status="PENDING_MANAGER_REVIEW", is_deleted=False).order_by('-id')
        for report in reports_1:
            report_total.append(report)
        reports_2 = model.objects.filter(created_by=self,status="PENDING_TEAM_LEADER_REVIEW", is_deleted=False).order_by('-id')
        for report in reports_2:
            report_total.append(report)
        return len(report_total)

    def get_published_reviews(self):
        model = apps.get_model('app', 'Inspection')
        reports = model.objects.filter(created_by=self,status="PUBLISHED", is_deleted=False).order_by('-id')
        return reports

    def get_complied_reviews(self):
        model = apps.get_model('app', 'Inspection')
        reports = model.objects.filter(created_by=self,status="COMPLIED", is_deleted=False).order_by('-id')
        return reports

    def get_rejected_reviews(self):
        model = apps.get_model('app', 'Inspection')
        reports = model.objects.filter(created_by=self,status="REJECTED", is_deleted=False).order_by('-id')
        return reports

    #staff reviews(get reviewer records) end

    




