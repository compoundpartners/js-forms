# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import submit_form_view, submit_form_view_protect

urlpatterns = [
    url(r'^$', submit_form_view_protect, name='aldryn_forms_submit_form'),
    url(r'^exempt/$', submit_form_view, name='aldryn_forms_submit_form_exempt'),
]
