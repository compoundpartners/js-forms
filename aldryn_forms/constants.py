# -*- coding: utf-8 -*-

from django.conf import settings

SHOW_ALL_RECIPIENTS = getattr(
    settings,
    'ALDRYN_FORMS_SHOW_ALL_RECIPIENTS',
    True,
)
ENABLE_API = getattr(
    settings,
    'ALDRYN_FORMS_ENABLE_API',
    False,
)
ENABLE_FORM_ID = getattr(
    settings,
    'ALDRYN_FORMS_ENABLE_FORM_ID',
    False,
)
ENABLE_LOCALSTORAGE = getattr(
    settings,
    'ALDRYN_FORMS_ENABLE_LOCALSTORAGE',
    False,
)
ENABLE_LOCALSTORAGE_COOKIE = getattr(
    settings,
    'ALDRYN_FORMS_ENABLE_LOCALSTORAGE_COOKIE',
    False,
)
ENABLE_LOCALSTORAGE_COOKIE_CONTAINS = getattr(
    settings,
    'ALDRYN_FORMS_ENABLE_LOCALSTORAGE_COOKIE_CONTAINS',
    False,
)
ENABLE_SIMPLE_FORMS = getattr(
    settings,
    'ALDRYN_FORMS_ENABLE_SIMPLE_FORMS',
    False,
)
ENABLE_FORM_TEMPLATE = getattr(
    settings,
    'ALDRYN_FORMS_ENABLE_FORM_TEMPLATE',
    False,
)
ENABLE_CUSTOM_CSS = getattr(
    settings,
    'ALDRYN_FORMS_ENABLE_CUSTOM_CSS',
    False,
)
DEFAULT_ACTION_BACKEND = getattr(
    settings,
    'ALDRYN_FORMS_DEFAULT_ACTION_BACKEND',
    'email_only',
)
RECAPTCHA_PUBLIC_KEY = getattr(
    settings,
    'RECAPTCHA_PUBLIC_KEY',
    None,
)
RECAPTCHA_PRIVATE_KEY = getattr(
    settings,
    'RECAPTCHA_PRIVATE_KEY',
    None,
)
RECAPTCHA_USE_V3 = getattr(
    settings,
    'RECAPTCHA_USE_V3',
    False,
)
MANDRILL_DEFAULT_TEMPLATE = getattr(
    settings,
    'MANDRILL_DEFAULT_TEMPLATE',
    None,
)
DO_NOT_SEND_NOTIFICATION_EMAIL_WHEN_USE_ACTION_BACKENDS = getattr(
    settings,
    'ALDRYN_FORMS_DO_NOT_SEND_NOTIFICATION_EMAIL_WHEN_USE_ACTION_BACKENDS',
    [],
)
CUSTOM_ACTION_BACKENDS = getattr(
    settings,
    'ALDRYN_FORMS_CUSTOM_ACTION_BACKENDS',
    {},
)
FORM_CUSTOM_FIELDS = getattr(
    settings,
    'ALDRYN_FORMS_FORM_CUSTOM_FIELDS',
    {},
)
COUNTER_FIELD_UNIQ = getattr(
    settings,
    'ALDRYN_FORMS_COUNTER_FIELD_UNIQ',
    False,
)

