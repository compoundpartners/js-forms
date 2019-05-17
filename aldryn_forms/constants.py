# -*- coding: utf-8 -*-

from django.conf import settings

SHOW_ALL_RECIPIENTS = getattr(
    settings,
    'ALDRYN_FORMS_SHOW_ALL_RECIPIENTS',
    True,
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
