# -*- coding: utf-8 -*-
from PIL import Image

from django import forms
from django.conf import settings
from django.forms.forms import NON_FIELD_ERRORS
from django.utils.translation import gettext, gettext_lazy as _

from .models import FormSubmission, FormPlugin
from .utils import add_form_error, get_user_model
from .constants import (
    DEFAULT_ACTION_BACKEND,
    FORM_CUSTOM_FIELDS
)

try:
    from js_custom_fields.forms import CustomFieldsFormMixin
except:
    class CustomFieldsFormMixin(object):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if 'custom_fields' in self.fields:
                self.fields['custom_fields'].widget = forms.HiddenInput()


class FileSizeCheckMixin(object):
    def __init__(self, *args, **kwargs):
        self.max_size = kwargs.pop('max_size', None)
        super(FileSizeCheckMixin, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(FileSizeCheckMixin, self).clean(*args, **kwargs)

        if data is None:
            return

        if self.max_size is not None and data.size > self.max_size:
            try:
                from sizefield.utils import filesizeformat
                max_size = filesizeformat(self.max_size)
                actual_size = filesizeformat(data.size)
            except ImportError:
                max_size = self.max_size
                actual_size = data.size
            raise forms.ValidationError(
                gettext('File size must be under %(max_size)s. Current file size is %(actual_size)s.') % {
                    'max_size': max_size,
                    'actual_size': actual_size,
                })
        return data


class RestrictedFileField(FileSizeCheckMixin, forms.FileField):
    pass


class RestrictedImageField(FileSizeCheckMixin, forms.ImageField):

    def __init__(self, *args, **kwargs):
        self.max_width = kwargs.pop('max_width', None)
        self.max_height = kwargs.pop('max_height', None)
        super(RestrictedImageField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(RestrictedImageField, self).clean(*args, **kwargs)

        if data is None or not any([self.max_width, self.max_height]):
            return data

        if hasattr(data, 'image'):
            # Django >= 1.8
            width, height = data.image.size
        else:
            width, height = Image.open(data).size
            # cleanup after ourselves
            data.seek(0)

        if self.max_width and width > self.max_width:
            raise forms.ValidationError(
                gettext(
                    'Image width must be under %(max_size)s pixels. '
                    'Current width is %(actual_size)s pixels.'
                ) % {
                    'max_size': self.max_width,
                    'actual_size': width,
                })

        if self.max_height and height > self.max_height:
            raise forms.ValidationError(
                gettext(
                    'Image height must be under %(max_size)s pixels. '
                    'Current height is %(actual_size)s pixels.'
                ) % {
                    'max_size': self.max_height,
                    'actual_size': height,
                })

        return data


class FormSubmissionBaseForm(forms.Form):

    # these fields are internal.
    # by default we ignore all hidden fields when saving form data to db.
    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        widget=forms.HiddenInput()
    )
    form_plugin_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.form_plugin = kwargs.pop('form_plugin')
        self.request = kwargs.pop('request')
        super(FormSubmissionBaseForm, self).__init__(*args, **kwargs)
        language = self.form_plugin.language

        self.instance = FormSubmission(
            name=self.form_plugin.name,
            language=language,
            form_url=self.request.build_absolute_uri(self.request.path),
        )
        self.fields['language'].initial = language
        self.fields['form_plugin_id'].initial = self.form_plugin.pk

    def _add_error(self, message, field=NON_FIELD_ERRORS):
        if not self._errors is None:
            try:
                self._errors[field].append(message)
            except KeyError:
                self._errors[field] = self.error_class([message])

    def get_serialized_fields(self, is_confirmation=False):
        """
        The `is_confirmation` flag indicates if the data will be used in a
        confirmation email sent to the user submitting the form or if it will be
        used to render the data for the recipients/admin site.
        """
        for field in self.form_plugin.get_form_fields():
            plugin = field.plugin_instance.get_plugin_class_instance()
            # serialize_field can be None or SerializedFormField  namedtuple instance.
            # if None then it means we shouldn't serialize this field.
            serialized_field = plugin.serialize_field(self, field, is_confirmation)

            if serialized_field:
                yield serialized_field

    def get_serialized_field_choices(self, is_confirmation=False):
        """Renders the form data in a format suitable to be serialized.
        """
        fields = self.get_serialized_fields(is_confirmation)
        fields = [(field.label, field.value) for field in fields]
        return fields

    def get_serialized_field_dict(self, is_confirmation=False):
        fields = self.get_serialized_fields(is_confirmation)
        fields = [(field.name, field.value) for field in fields]
        return dict(fields)

    def get_cleaned_data(self, is_confirmation=False):
        fields = self.get_serialized_fields(is_confirmation)
        form_data = dict((field.name, field.value) for field in fields)
        return form_data

    def save(self, commit=False):
        self.instance.set_form_data(self)
        self.instance.save()

    def clean_recipients(self):
        recipients = self.cleaned_data['recipients']
        action_backend = self.cleaned_data['action_backend']
        action_backend = DEFAULT_ACTION_BACKEND if action_backend == 'default' else action_backend
        if 'email' in action_backend and not recipients:
            raise forms.ValidationError("Please select recipients")
        return recipients


class ExtandableErrorForm(forms.ModelForm):

    def append_to_errors(self, field, message):
        add_form_error(form=self, message=message, field=field)


class CheckNameMixin(object):

    def clean_name(self):
        data = self.cleaned_data['name']
        if '-' in data or ' ' in data:
            raise forms.ValidationError("Please fix field name")
        if False and data:
            instance = self.instance
            form_plugin = instance.get_form_plugin()
            if form_plugin:
                plugins = form_plugin.get_form_elements()
                if plugins:
                    for plugin in plugins:
                        if hasattr(plugin, 'name') and plugin.name == data and self.instance.pk != plugin.pk:
                            raise forms.ValidationError("Filed name is not unique")
        return data


class FormPluginForm(CustomFieldsFormMixin, ExtandableErrorForm):

    custom_fields = 'get_custom_fields'

    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs:
            kwargs['initial']['action_backend'] = DEFAULT_ACTION_BACKEND

        super(FormPluginForm, self).__init__(*args, **kwargs)

        if (getattr(settings, 'ALDRYN_FORMS_SHOW_ALL_RECIPIENTS', False) and
                'recipients' in self.fields):
            self.fields['recipients'].queryset = get_user_model().objects.all()

    def clean(self):
        redirect_type = self.cleaned_data.get('redirect_type')
        redirect_page = self.cleaned_data.get('redirect_page')
        url = self.cleaned_data.get('url')

        if redirect_type:
            if redirect_type == FormPlugin.REDIRECT_TO_PAGE:
                if not redirect_page:
                    self.append_to_errors('redirect_page', _('Please provide CMS page for redirect.'))
                self.cleaned_data['url'] = None

            if redirect_type == FormPlugin.REDIRECT_TO_URL:
                if not url:
                    self.append_to_errors('url', _('Please provide an absolute URL for redirect.'))
                self.cleaned_data['redirect_page'] = None
        else:
            self.cleaned_data['url'] = None
            self.cleaned_data['redirect_page'] = None

        return self.cleaned_data

    def get_custom_fields(self):
        return FORM_CUSTOM_FIELDS


class BooleanFieldForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs:  # creating new one
            initial = kwargs.pop('initial', {})
            initial['required'] = False
            kwargs['initial'] = initial
        super(BooleanFieldForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['label', 'help_text', 'required', 'required_message', 'custom_classes']


class SelectFieldForm(forms.ModelForm):

    class Meta:
        fields = ['label', 'help_text', 'required', 'required_message', 'custom_classes']


class RadioFieldForm(forms.ModelForm):

    class Meta:
        fields = ['label', 'help_text', 'required', 'required_message', 'custom_classes']


class CaptchaFieldForm(forms.ModelForm):

    class Meta:
        # captcha is always required
        fields = ['label', 'help_text', 'required_message']


class MinMaxValueForm(ExtandableErrorForm):

    def clean(self):
        min_value = self.cleaned_data.get('min_value')
        max_value = self.cleaned_data.get('max_value')
        if min_value and max_value and min_value > max_value:
            self.append_to_errors('min_value', _(u'Min value can not be greater than max value.'))
        return self.cleaned_data


class TextFieldForm(CheckNameMixin, MinMaxValueForm):

    def __init__(self, *args, **kwargs):
        super(TextFieldForm, self).__init__(*args, **kwargs)

        self.fields['min_value'].label = _(u'Min length')
        self.fields['min_value'].help_text = _(u'Required number of characters to type.')

        self.fields['max_value'].label = _(u'Max length')
        self.fields['max_value'].help_text = _(u'Maximum number of characters to type.')
        self.fields['max_value'].required = False

    class Meta:
        fields = ['label', 'placeholder_text', 'help_text',
                  'min_value', 'max_value', 'required', 'required_message', 'custom_classes']


class HiddenFieldForm(ExtandableErrorForm):
    class Meta:
        fields = ['name', 'initial_value']


class EmailFieldForm(TextFieldForm):

    def __init__(self, *args, **kwargs):
        super(EmailFieldForm, self).__init__(*args, **kwargs)
        self.fields['min_value'].required = False
        self.fields['max_value'].required = False

    class Meta:
        fields = [
            'label',
            'placeholder_text',
            'help_text',
            'min_value',
            'max_value',
            'required',
            'required_message',
            'email_send_notification',
            'email_subject',
            'email_body',
            'custom_classes',
        ]


class MandrillEmailFieldForm(TextFieldForm):

    def __init__(self, *args, **kwargs):
        super(MandrillEmailFieldForm, self).__init__(*args, **kwargs)
        self.fields['min_value'].required = False
        self.fields['max_value'].required = False

    class Meta:
        fields = [
            'label',
            'placeholder_text',
            'help_text',
            'min_value',
            'max_value',
            'required',
            'required_message',
            'email_send_notification',
            'email_subject',
            'email_body',
            'email_template_name',
            'custom_classes',
        ]


class FileFieldForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FileFieldForm, self).__init__(*args, **kwargs)
        self.fields['help_text'].help_text = _(
            'Explanatory text displayed next to input field. Just like this '
            'one. You can use MAXSIZE as a placeholder for the maximum size '
            'configured below.')

    class Meta:
        fields = ['label', 'help_text', 'required', 'required_message',
                  'custom_classes', 'upload_to', 'max_size']


class ImageFieldForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImageFieldForm, self).__init__(*args, **kwargs)
        self.fields['help_text'].help_text = _(
            'Explanatory text displayed next to input field. Just like this '
            'one. You can use MAXSIZE, MAXWIDTH, MAXHEIGHT as a placeholders '
            'for the maximum file size and dimensions configured below.')

    class Meta:
        fields = FileFieldForm.Meta.fields + ['max_height', 'max_width']


class TextAreaFieldForm(TextFieldForm):

    def __init__(self, *args, **kwargs):
        super(TextAreaFieldForm, self).__init__(*args, **kwargs)
        self.fields['max_value'].required = False

    class Meta:
        fields = ['label', 'placeholder_text', 'help_text', 'text_area_columns',
                  'text_area_rows', 'min_value', 'max_value', 'required', 'required_message', 'custom_classes']


class MultipleSelectFieldForm(MinMaxValueForm):

    def __init__(self, *args, **kwargs):
        super(MultipleSelectFieldForm, self).__init__(*args, **kwargs)

        self.fields['min_value'].label = _(u'Min choices')
        self.fields['min_value'].help_text = _(u'Required amount of elements to chose.')

        self.fields['max_value'].label = _(u'Max choices')
        self.fields['max_value'].help_text = _(u'Maximum amount of elements to chose.')

    class Meta:
        # 'required' and 'required_message' depend on min_value field validator
        fields = ['label', 'help_text', 'min_value', 'max_value', 'custom_classes']
