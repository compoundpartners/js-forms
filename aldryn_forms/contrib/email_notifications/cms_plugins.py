# -*- coding: utf-8 -*-
import logging
from functools import partial

from email.utils import parseaddr

MANDRILL = False
try:
    from mandrillit.api import send_constructed_mail
    MANDRILL = True
except ImportError:
    pass

from django.contrib import admin
from django.core.mail import get_connection
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from cms.plugin_pool import plugin_pool

from aldryn_forms.cms_plugins import FormPlugin
from aldryn_forms.validators import is_valid_recipient
from aldryn_forms.constants import (
    ENABLE_FORM_TEMPLATE,
    ENABLE_CUSTOM_CSS,
    MANDRILL_DEFAULT_TEMPLATE,
    ENABLE_LOCALSTORAGE,
    ENABLE_FORM_ID,
)
from .notification import DefaultNotificationConf
from .models import EmailNotification, FieldConditional, EmailNotificationFormPlugin
from . import forms


logger = logging.getLogger(__name__)


class NewEmailNotificationInline(admin.StackedInline):
    extra = 1
    fields = ['theme']
    model = EmailNotification
    verbose_name = _('add new email notification')
    verbose_name_plural = _('add new email notifications')

    fieldsets = (
        (None, {
            'fields': (
                'theme',
            )
        }),
    )

    def get_queryset(self, request):
        queryset = super(NewEmailNotificationInline, self).get_queryset(request)
        return queryset.none()


class ExistingEmailNotificationInline(admin.StackedInline):
    model = EmailNotification

    fieldsets = (
        (None, {
            'fields': (
                'theme',
            )
        }),
        (_('Recipients'), {
            'classes': ('collapse',),
            'fields': (
                'text_variables',
                'to_user',
                ('to_name', 'to_email'),
                ('from_name', 'from_email'),
            )
        }),
    )

    readonly_fields = ['text_variables']
    text_variables_help_text = _('variables can be used with by '
                                 'wrapping with "${variable}" like ${variable}')

    def get_formset(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super(ExistingEmailNotificationInline, self).get_formset(request, obj, **kwargs)


    def formfield_for_dbfield(self, db_field, request, **kwargs):
        obj = kwargs.pop('obj', None)
        if obj and db_field.name == 'to_user':
            kwargs['queryset'] = obj.recipients.all()
            return super(ExistingEmailNotificationInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        return super(ExistingEmailNotificationInline, self).formfield_for_dbfield(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return False

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(ExistingEmailNotificationInline, self).get_fieldsets(request, obj)

        if obj is None:
            return fieldsets

        email_fieldset = self.get_email_fieldset(obj)
        fieldsets = list(fieldsets) + email_fieldset
        return fieldsets

    def get_email_fieldset(self, obj):
        fields = ['subject']

        notification_conf = obj.get_notification_conf()

        if notification_conf.txt_email_format_configurable:
            # add the body_text field only if it's configurable
            fields.append('body_text')

        if notification_conf.html_email_format_enabled:
            # add the body_html field only if email is allowed
            # to be sent in html version.
            fields.append('body_html')
        return [(_('Email'), {
            'classes': ('collapse',),
            'fields': fields
        })]

    def text_variables(self, obj):
        if obj.pk is None:
            return ''

        # list of tuples - [('category', [('value', 'label')])]
        choices_by_category = obj.form.get_notification_text_context_keys_as_choices()

        li_items = []

        for category, choices in choices_by_category:
            # <li>field_1</li><li>field_2</li>
            fields_li = u''.join((u'<li>{0} | {1}</li>'.format(*var) for var in choices))

            if fields_li:
                li_item = u'<li>{0}</li><ul>{1}</ul>'.format(category, fields_li)
                li_items.append(li_item)
        unordered_list = u'<ul>{0}</ul>'.format(u''.join(li_items))
        help_text = u'<p class="help">{0}</p>'.format(self.text_variables_help_text)
        return mark_safe(unordered_list + u'\n' + help_text)
    text_variables.allow_tags = True
    text_variables.short_description = _('available text variables')


class NewFieldConditionalInline(admin.StackedInline):
    extra = 1
    fields = ['field_name']
    model = FieldConditional
    form = forms.FieldConditionalForm
    verbose_name = _('new conditional')
    verbose_name_plural = _('new conditionals')

    fieldsets = (
        (None, {
            'fields': (
                'field_name',
            )
        }),
    )

    def get_queryset(self, request):
        queryset = super(NewFieldConditionalInline, self).get_queryset(request)
        return queryset.none()

    def get_formset(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super(NewFieldConditionalInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'field_name':
            choices = [('','-----------')]
            obj = kwargs.pop('obj', None)
            if obj:
                for field in obj.get_form_fields():
                    if hasattr(field.plugin_instance, 'option_set') and field.plugin_instance.option_set.exists():
                        choices.append((field.name, field.label))
            kwargs['widget'].choices = choices
        return super(NewFieldConditionalInline, self).formfield_for_choice_field(db_field, request, **kwargs)

class ExistingFieldConditionalInline(admin.StackedInline):
    model = FieldConditional
    form = forms.FieldConditionalForm

    fieldsets = (
        (None, {
            'fields': (
                'field_value',
                'action_type',
                'action_value'
            )
        }),
    )

    readonly_fields = ['field_name_text']

    def has_add_permission(self, request):
        return False


class EmailNotificationForm(FormPlugin):
    name = _('Advanced Form')
    model = EmailNotificationFormPlugin
    form = forms.EmailNotificationFormPluginForm
    inlines = [
        ExistingEmailNotificationInline,
        NewEmailNotificationInline,
        ExistingFieldConditionalInline,
        NewFieldConditionalInline
    ]
    notification_conf_class = DefaultNotificationConf

    advanced_fields = (
        'redirect_type',
        ('redirect_page', 'url'),
    )
    if ENABLE_FORM_TEMPLATE:
        advanced_fields = (
            'form_template',
        )
    if ENABLE_CUSTOM_CSS:
        advanced_fields = (
            'custom_classes',
        )

    main_fields = [
        'name',
        'form_id',
        'success_message',
        'error_message',
        'action_backend',
        'form_type',
        'download_file',
        'recipients',
        'custom_fields',
    ]
    if not ENABLE_FORM_ID:
        main_fields.remove('form_id')

    fieldsets = (
        (None, {
            'fields': main_fields
        }),
        (_('Redirect to'), {
            'classes': ('collapse',),
            'fields': advanced_fields
        }),
    )

    def get_inline_instances(self, request, obj=None):
        inlines = super(EmailNotificationForm, self).get_inline_instances(request, obj)

        if obj is None:
            # remove ExistingEmailNotificationInline inline instance
            # if we're first creating this object.
            inlines = [inline for inline in inlines
                       if isinstance(inline, (NewEmailNotificationInline, NewFieldConditionalInline))]
        return inlines

    def send_notifications(self, instance, form, request=None):
        recipients = []
        emails = []
        if not MANDRILL:
            try:
                connection = get_connection(fail_silently=False)
                connection.open()
            except:  # noqa
                # I use a "catch all" in order to not couple this handler to a specific email backend
                # different email backends have different exceptions.
                logger.exception("Could not send notification emails.")
                return []

        conditionals = self.get_conditionals(instance, form, 'email')
        if conditionals:
            for conditional in conditionals:
                emails.append(conditional.prepare_email(form=form))
                recipients.append(parseaddr(conditional.action_value))

        redirect_emails = self.get_conditionals(instance, form, 'redirect-email')
        if redirect_emails:
            for conditional in redirect_emails:
                emails.append(conditional.prepare_email(form=form))
                recipients.append(parseaddr(conditional.action_value))
        else:
            recipients = super(EmailNotificationForm, self).send_notifications(instance, form, request)
            notifications = instance.email_notifications.select_related('form')

            for notification in notifications:
                email = notification.prepare_email(form=form)
                copy_email = notification.prepare_copy_email(form=form)

                to_email = email['to'][0]['email'] if MANDRILL else email.to[0]
                to_copy_email = copy_email['to'][0]['email'] if MANDRILL else copy_email.to[0]


                if is_valid_recipient(to_email):
                    emails.append(email)
                    recipients.append(parseaddr(to_email))
                if to_email != to_copy_email and is_valid_recipient(to_copy_email):
                    emails.append(copy_email)
                    recipients.append(parseaddr(to_copy_email))


        if MANDRILL:
            for email in emails:
                send_constructed_mail(email, MANDRILL_DEFAULT_TEMPLATE)
            return recipients
        else:
            try:
                connection.send_messages(emails)
            except:  # noqa
                # again, we catch all exceptions to be backend agnostic
                logger.exception("Could not send notification emails.")
                recipients = []
            return recipients

    def render(self, context, instance, placeholder):
        context = super(EmailNotificationForm, self).render(context, instance, placeholder)
        request = context['request']

        form = self.process_form(instance, request)

        if form.is_valid():
            context['post_success'] = True
            conditionals = self.get_conditionals(instance, form, 'redirect')
            if conditionals:
                context['form_success_url'] = conditionals[0].action_value
            else:
                context['form_success_url'] = self.get_success_url(instance)
        context['form'] = form
        if instance.get_gated_content_container and request.GET.get('noform') == 'true':
            context['post_success'] = True
        context['enable_localstorage'] = ENABLE_LOCALSTORAGE
        return context

    def get_conditionals(self, instance, form, action_type):
        conditionals = []
        form_data = form.get_serialized_field_dict()
        for c in instance.conditionals.select_related('form'):
            value = form_data.get(c.field_name)
            if c.action_type == action_type and value and c.field_value in value.split(', '):
                if action_type in ['email', 'redirect-email']:
                     if is_valid_recipient(c.action_value):
                         conditionals.append(c)
                else:
                    conditionals.append(c)
        return conditionals


plugin_pool.register_plugin(EmailNotificationForm)
