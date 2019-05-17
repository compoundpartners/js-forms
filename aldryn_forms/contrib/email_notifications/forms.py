# -*- coding: utf-8 -*-
from django import forms
from aldryn_forms.forms import FormPluginForm
from . import models

class EmailNotificationFormPluginForm(FormPluginForm):

    def __init__(self, *args, **kwargs):
        super(EmailNotificationFormPluginForm, self).__init__(*args, **kwargs)
        self.fields['error_message'].required = True
        self.fields['success_message'].required = True


class FieldConditionalForm(forms.ModelForm):

    class Meta:
        #model = models.FieldConditional
        widgets = {
            'field_name': forms.Select(),
            'field_vale': forms.Select(),
        }
