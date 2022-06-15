# -*- coding: utf-8 -*-
import logging

from django.utils.translation import ugettext_lazy as _

from .action_backends_base import BaseAction

logger = logging.getLogger(__name__)

try:
    from custom.aldryn_forms.api import APIMixin
except:
    class APIMixin(object):
        def form_valid(self, cmsplugin, instance, request, form):
            raise NotImplementedError('Please create API mixin in custom.aldryn_forms.api')


class DefaultAction(BaseAction):
    verbose_name = _('Email and save')

    def form_valid(self, cmsplugin, instance, request, form):
        recipients = cmsplugin.send_notifications(instance, form, request)
        form.instance.set_recipients(recipients)
        form.save()
        cmsplugin.send_success_message(instance, request)


class EmailAction(BaseAction):
    verbose_name = _('Email only')

    def form_valid(self, cmsplugin, instance, request, form):
        recipients = cmsplugin.send_notifications(instance, form, request)
        logger.info('Sent email notifications to {} recipients.'.format(len(recipients)))


class NoAction(BaseAction):
    verbose_name = _('None')

    def form_valid(self, cmsplugin, instance, request, form):
        form_id = form.form_plugin.id
        logger.info('Not persisting data for "{}" since action_backend is set to "none"'.format(form_id))


class EmailAPIAction(APIMixin, BaseAction):
    verbose_name = _('Email and API')

    def form_valid(self, cmsplugin, instance, request, form):
        recipients = cmsplugin.send_notifications(instance, form, request)
        try:
            super().form_valid(cmsplugin, instance, request, form)
        except:
            form.instance.set_recipients(recipients)
            form.save()
        cmsplugin.send_success_message(instance, request)

    def form_invalid(self, cmsplugin, instance, request, form):
        pass


class APIAction(APIMixin, BaseAction):
    verbose_name = _('API Only')

    def form_valid(self, cmsplugin, instance, request, form):
        try:
            super().form_valid(cmsplugin, instance, request, form)
        except:
            recipients = cmsplugin.send_notifications(instance, form, request)
            form.instance.set_recipients(recipients)
            form.save()
        cmsplugin.send_success_message(instance, request)

    def form_invalid(self, cmsplugin, instance, request, form):
        pass
