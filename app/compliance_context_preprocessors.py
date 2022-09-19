import json
import os
from os import path
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
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

from app.forms import *

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

def notifications(type,heading,message):
    context = {type,heading,message}
    return context
