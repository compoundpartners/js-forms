# -*- coding: utf-8 -*-
from email.utils import formataddr
from functools import partial

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext, gettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField

from aldryn_forms.helpers import get_user_name
from aldryn_forms.models import FormPlugin

try:
    from mandrillit.api import construct_mail
except ImportError:
    from emailit.api import construct_mail

from .helpers import (
    get_email_template_name,
    get_theme_template_name,
    render_text
)
from aldryn_forms.constants import DO_NOT_SEND_NOTIFICATION_EMAIL_WHEN_USE_ACTION_BACKENDS

EMAIL_THEMES = getattr(
    settings,
    "ALDRYN_FORMS_EMAIL_THEMES",
    [('default', _('default'))]
)
ACTION_TYPES = (
    ('email', 'CC Email to'),
    ('redirect-email', 'Redirect email to'),
    ('redirect', 'Redirect to'),
)


class EmailNotificationFormPlugin(FormPlugin):

    class Meta:
        proxy = True

    def copy_relations(self, oldinstance):
        for recipient in oldinstance.recipients.all():
            self.recipients.add(recipient)
        for item in oldinstance.email_notifications.all():
            item.pk = None
            item.form = self
            item.save()
        for item in oldinstance.conditionals.all():
            item.pk = None
            item.form = self
            item.save()

    def get_notification_conf(self):
        plugin_class = self.get_plugin_class()
        return plugin_class.notification_conf_class(form_plugin=self)

    def get_notification_text_context(self, form):
        notification_conf = self.get_notification_conf()
        text_context = notification_conf.get_context(form)
        return text_context

    def get_notification_text_context_keys_as_choices(self):
        notification_conf = self.get_notification_conf()
        choices = notification_conf.get_context_keys_as_choices()
        return choices


class EmailNotification(models.Model):

    class Meta:
        verbose_name = _('Email notification')
        verbose_name_plural = _('Email notifications')

    theme = models.CharField(
        verbose_name=_('theme'),
        max_length=200,
        help_text=_('Provides the base theme for the email.'),
        choices=EMAIL_THEMES
    )
    to_name = models.CharField(
        verbose_name=_('to name'),
        max_length=200,
        blank=True
    )
    to_email = models.CharField(
        verbose_name=_('to email'),
        max_length=200,
        blank=True
    )
    to_user = models.ForeignKey(
        to=getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        on_delete=models.SET_NULL,
        verbose_name=_('to user'),
        blank=True,
        null=True,
        limit_choices_to={'is_staff': True},
    )
    from_name = models.CharField(
        verbose_name=_('from name'),
        max_length=200,
        blank=True
    )
    from_email = models.CharField(
        verbose_name=_('from email'),
        max_length=200,
        blank=True,
        help_text='Must be from a verified domain'
    )
    subject = models.CharField(
        verbose_name=_("subject"),
        max_length=200,
        blank=True
    )
    body_text = models.TextField(
        verbose_name=_('email body (txt)'),
        blank=True,
        help_text=_('used when rendering the email in text only mode.')
    )
    body_html = HTMLField(
        verbose_name=_('email body (html)'),
        blank=True,
        help_text=_('used when rendering the email in html.')
    )
    form = models.ForeignKey(
        to=EmailNotificationFormPlugin,
        on_delete=models.CASCADE,
        related_name='email_notifications'
    )

    def __str__(self):
        to_name = self.get_recipient_name()
        to_email = self.get_recipient_email()
        return u'{0} ({1})'.format(to_name, to_email)

    def clean(self):
        recipient_email = self.get_recipient_email()
        if self.pk and not recipient_email:
            message = gettext('Please provide a recipient.')
            raise ValidationError(message)
        if self.pk and self.body_html and not self.body_text:
            import html2text
            h = html2text.HTML2Text()
            h.reference_links = False
            self.body_text = h.handle(self.body_html)


    def get_recipient_name(self):
        if self.to_name:
            # manual name takes precedence over user relationship.
            name = self.to_name
        #elif self.to_user_id:
        #    name = get_user_name(self.to_user)
        else:
            name = ''
        return name

    def get_recipient_email(self):
        if self.to_email:
            # manual email takes precedence over user relationship.
            email = self.to_email
        elif self.to_user_id:
            email = self.to_user.email
        else:
            email = ''
        return email

    def get_email_context(self, form):
        get_template = partial(get_theme_template_name, theme=self.theme)

        context = {
            'form_plugin': self.form,
            'form_data': form.get_serialized_field_choices(is_confirmation=True),
            'form_name': self.form.name,
            'email_notification': self,
            'email_html_theme': get_template(suffix='html'),
            'email_txt_theme': get_template(suffix='txt'),
        }
        return context

    def get_email_kwargs(self, form):
        form_plugin = self.form

        text_context = form_plugin.get_notification_text_context(form)

        email_context = self.get_email_context(form)
        email_context['text_context'] = text_context

        notification_conf = form_plugin.get_notification_conf()

        kwargs = {
            'context': email_context,
            'language': form_plugin.language,
            # needs to be empty string because emailit expects a string
            # it's empty so the template lookup fails.
            'template_base': '',
            'body_templates': [
                notification_conf.get_txt_email_template_name()],
            'subject_templates': [
                get_email_template_name(name='subject', suffix='txt')],
        }

        if notification_conf.html_email_format_enabled:
            # we only want to render html template if html format is enabled.
            kwargs['html_templates'] = [
                notification_conf.get_html_email_template_name()]

        render = partial(render_text, context=text_context)

        recipient_name = self.get_recipient_name()

        recipient_email = self.get_recipient_email()

        if not self.form.action_backend in DO_NOT_SEND_NOTIFICATION_EMAIL_WHEN_USE_ACTION_BACKENDS:
            recipient_email = render(recipient_email)

        if recipient_name:
            recipient_name = render(recipient_name)
            recipient_email = formataddr((recipient_name, recipient_email))

        kwargs['recipients'] = [recipient_email]

        if self.from_email:
            from_email = render(self.from_email)

            if self.from_name:
                from_name = render(self.from_name)
                from_email = formataddr((from_name, from_email))

            kwargs['from_email'] = from_email
            kwargs['reply_to'] = [from_email]
        return kwargs

    def get_copy_email_kwargs(self, form):
        kwargs = self.get_email_kwargs(form)
        if self.to_user_id:
            kwargs['recipients'] = [self.to_user.email]
        return kwargs


    def prepare_email(self, form):
        email_kwargs = self.get_email_kwargs(form)
        return construct_mail(**email_kwargs)

    def prepare_copy_email(self, form):
        email_kwargs = self.get_copy_email_kwargs(form)
        return construct_mail(**email_kwargs)

    def render_body_text(self, context):
        return render_text(self.body_text, context)

    def render_body_html(self, context):
        return render_text(self.body_html, context)

    def render_subject(self, context):
        return render_text(self.subject, context)


class FieldConditional(models.Model):

    class Meta:
        verbose_name = _('conditional')
        verbose_name_plural = _('conditionals')

    field_name = models.CharField(
        verbose_name=_('field'),
        max_length=255,
    )
    field_value = models.CharField(
        verbose_name=_('field value'),
        max_length=255,
    )
    action_type = models.CharField(
        verbose_name=_('action'),
        max_length=20,
        choices=ACTION_TYPES
    )
    action_value = models.CharField(
        verbose_name=_('to name'),
        max_length=255,
    )
    form = models.ForeignKey(
        to=EmailNotificationFormPlugin,
        on_delete=models.CASCADE,
        related_name='conditionals'
    )

    def __str__(self):
        if self.form:
            field = self.form.get_form_fields_by_name().get(self.field_name)
            if field:
                return field.label or self.field_name
        return self.field_name

    def get_recipient_name(self):
        return self.action_value

    def get_recipient_email(self):
        return self.action_value

    def get_email_context(self, form):
        get_template = partial(get_theme_template_name, theme='default')

        context = {
            'form_plugin': self.form,
            'form_data': form.get_serialized_field_choices(is_confirmation=True),
            'form_name': self.form.name,
            'email_notification': self,
            'email_html_theme': get_template(suffix='html'),
            'email_txt_theme': get_template(suffix='txt'),
        }
        return context

    def get_email_kwargs(self, form):
        form_plugin = self.form

        text_context = form_plugin.get_notification_text_context(form)

        email_context = self.get_email_context(form)
        email_context['text_context'] = text_context

        notification_conf = form_plugin.get_notification_conf()

        kwargs = {
            'context': email_context,
            'language': form_plugin.language,
            # needs to be empty string because emailit expects a string
            # it's empty so the template lookup fails.
            'template_base': '',
            'body_templates': [
                notification_conf.get_txt_email_template_name()],
            'subject_templates': [
                get_email_template_name(name='subject', suffix='txt')],
        }

        if notification_conf.html_email_format_enabled:
            # we only want to render html template if html format is enabled.
            kwargs['html_templates'] = [
                notification_conf.get_html_email_template_name()]

        render = partial(render_text, context=text_context)

        recipient_name = self.get_recipient_name()

        recipient_email = self.get_recipient_email()
        recipient_email = render(recipient_email)

        if recipient_name:
            recipient_name = render(recipient_name)
            recipient_email = formataddr((recipient_name, recipient_email))

        kwargs['recipients'] = [recipient_email]

        return kwargs

    def prepare_email(self, form):
        email_kwargs = self.get_email_kwargs(form)
        return construct_mail(**email_kwargs)

    def render_body_text(self, context):
        return ''

    def render_body_html(self, context):
        return ''

    def render_subject(self, context):
        return ''
