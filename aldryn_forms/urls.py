# -*- coding: utf-8 -*-
from django.urls import re_path

from .views import submit_form_view, submit_form_view_protect

urlpatterns = [
    re_path(r'^$', submit_form_view_protect, name='aldryn_forms_submit_form'),
    re_path(r'^exempt/$', submit_form_view, name='aldryn_forms_submit_form_exempt'),
]
