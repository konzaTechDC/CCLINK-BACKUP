"""
Django settings for ComplianceReporting project.

Based on 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import json
import posixpath
from celery.schedules import crontab
#import ComplianceReporting.tasks as tasks

# Sentry Monitoring imports
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Sentry Monitoring Config
sentry_sdk.init(
    dsn="https://cd6415c1b85d42d8881d6da943c4067a@o1133111.ingest.sentry.io/6195064",
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
#end sentry config


with open('/etc/config.json') as config_file:
    config = json.load(config_file)
    
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['kotdacompliance.konza.go.ke', '41.76.175.136']

AUTH_USER_MODEL  = 'user_auth.User'

# Application references
# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-INSTALLED_APPS
INSTALLED_APPS = [
    'app',
    'user_auth.apps.UserAuthConfig',
    'compliance.apps.ComplianceConfig',
    'crispy_forms',
    'phonenumber_field',
    'jsignature',
    'ComplianceReporting',
    #'user_auth',
    # Add your apps here to enable them
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Middleware framework
# https://docs.djangoproject.com/en/2.1/topics/http/middleware/
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #user defined middleware
    #'djdev_panel.middleware.DebugMiddleware',
]

ROOT_URLCONF = 'ComplianceReporting.urls'

# Template configuration
# https://docs.djangoproject.com/en/2.1/topics/templates/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.compliance_context_preprocessors.get_default_objects',
            ],
        },
    },
]

WSGI_APPLICATION = 'ComplianceReporting.wsgi.application'
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/etc/mysql/my.cnf',
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

#STATIC_ROOT = posixpath.join(*(BASE_DIR.split(os.path.sep) + ['static']))
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'app/static'),
    os.path.join(BASE_DIR, 'static/app'),
]
MEDIA_ROOT =  os.path.join(BASE_DIR, 'media') 
MEDIA_URL = '/media/'

'''
#email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.live.com'
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER =  "compliance@konza.go.ke"
# config['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = "#Kompliansi_2020**"
# ['EMAIL_HOST_PASSWORD']
SERVER_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
'''
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER =  "kotdacompliance@gmail.com"
EMAIL_HOST_PASSWORD = "#Kompliansi_2020**"

#choices items=============================================#############
#designation types#################
DESIGNATION_TYPES=[
    ('Construction Manager','Construction Manager'),
    ('Lead Consultant','Lead Consultant'),
    ('Lead ICT Engineer','Lead ICT Engineer'),
    ]

#personnel types
PERSONNEL_TYPES=[
    ('CONSTRUCTION SUPERVISING CONSULTANT’S PROFFESSIONALS','CONSTRUCTION SUPERVISING CONSULTANT’S PROFFESSIONALS'),
    ('CONSTRUCTION CONTRACTOR’S PERSONNEL','CONSTRUCTION CONTRACTOR’S PERSONNEL'),
    ]

PERSONNEL_DOCUMENT_TYPE=[
    ('Professional Practicing licence','Professional Practicing licence'),
    ('Work Permit','Work Permit'),
    ('Other','Other'),
    ]

COMPLIANCE_RECORD_TYPE=[
    ('Construction','Construction'),
    ('ICT','ICT'),
    ]

COMPLIANCE_MODULE_TYPE = [
    ('Quality Assurance','Quality Assurance'),
    ('Environmental Management','Environmental Management'),
    ('Traffic Management','Traffic Management'),
    ('Health and Safety','Health and Safety'),
    ('Security Management','Security Management')
    ]

COMPLIANCE_REQUIREMENT_METRIC_TYPE = [
    ('TYPE', 'TYPE'),
    ('QUANTITY', 'QUANTITY'),
    ('DISPOSAL', 'DISPOSAL'),
    ('Request For Information (RFI)', 'Request For Information (RFI)'),
    ('Material Approval (MA)', 'Material Approval (MA)'),
    ('TEST RESULT', 'TEST RESULT'),
    ('NUMBER OF APPROVALS/EXPECTED TEST RESULTS', 'NUMBER OF APPROVALS/EXPECTED TEST RESULTS'),
    ('NUMBER OF NON-APPROVALS', 'NUMBER OF NON-APPROVALS'),
    ]

COMPLIANCE_METRIC_INPUT_TYPE = [
    ('text','text'),
    ('int','int'),
    ]

PUBLISH_STATUS = [
    ('draft','draft'),
    ('pending','pending'),
    ('acknowledged','acknowledged'),
    ('rejected','rejected'),
    ]

MONTH_CHOICES = [
    ('January','January'),
    ('February','February'),
    ('March','March'),
    ('April','April'),
    ('May','May'),
    ('June','June'),
    ('July','July'),
    ('August','August'),
    ('September','September'),
    ('October','October'),
    ('November','November'),
    ('December','December'),
    ]


COMPLIANCE_INSPECTION_COMMENT_TYPE = [
    ('MEMBER','MEMBER'),
    ('TEAM_LEADER','TEAM_LEADER'),
    ('MANAGER','MANAGER'),
    ('CHIEF_MANAGER','CHIEF_MANAGER'),#power to rule hahahahahahahaha.... cough cough cough, minion hands over handkerchief
    ('CONTRACTOR','CONTRACTOR'),
    ]

COMPLIANCE_INSPECTION_STATUS = [
    ('DRAFT','DRAFT'),
    ('PENDING_TEAM_LEADER_REVIEW','PENDING_TEAM_LEADER_REVIEW'),
    ('PENDING_MANAGER_REVIEW','PENDING_MANAGER_REVIEW'),
    ('PUBLISHED','PUBLISHED'),
    ('COMPLIED','COMPLIED'),
    ('REJECTED','REJECTED'),
    ('DELETED','DELETED'),
    ]


CRISPY_TEMPLATE_PACK = 'bootstrap4'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'



# CELERY STUFF
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Nairobi'
CELERY_TASK_TRACK_STARTED = True


CELERY_IMPORTS = (
    'ComplianceReporting.celery',
    'ComplianceReporting.tasks',
    'ComplianceReporting',
)

CSRF_COOKIE_SECURE = False #to avoid transmitting the CSRF cookie over HTTP accidentally.
SESSION_COOKIE_SECURE = False #to avoid transmitting the session cookie over HTTP accidentally.

CSRF_COOKIE_SECURE = False #to avoid transmitting the CSRF cookie over HTTP accidentally.
SESSION_COOKIE_SECURE = False #to avoid transmitting the session cookie over HTTP accidentally.

SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

SECURE_SSL_REDIRECT = False
