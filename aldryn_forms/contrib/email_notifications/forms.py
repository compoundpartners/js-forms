# -*- coding: utf-8 -*-
from django import forms
from aldryn_forms.forms import FormPluginForm
from . import models

class EmailNotificationFormPluginForm(FormPluginForm):

    def __init__(self, *args, **kwargs):
        super(EmailNotificationFormPluginForm, self).__init__(*args, **kwargs)
        self.fields['error_message'].required = True
        self.fields['success_message'].required = True

    def clean_recipients(self):
        data = self.cleaned_data['recipients']
        if not data:
            raise forms.ValidationError("Please select recipients")
        return data


class FieldConditionalForm(forms.ModelForm):

    class Meta:
        #model = models.FieldConditional
        widgets = {
            'field_name': forms.Select(),
            'field_vale': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super(FieldConditionalForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.form:
            field = self.instance.form.get_form_fields_by_name().get(self.instance.field_name)
            if field:
                self.fields['field_value'].widget = forms.Select(choices=[['', '--------------']]+[[item.value, item.value] for item in field.plugin_instance.option_set.all()])
