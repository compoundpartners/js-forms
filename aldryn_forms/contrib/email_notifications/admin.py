# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
try:
    from django.core.urlresolvers import reverse
except ImportError:
    # Django 2.0
    from django.urls import reverse
from django.db.models import Count
from django.template.response import TemplateResponse
from django.utils.html import format_html
from .models import EmailNotificationFormPlugin

from django.conf import settings
PLUGINS_COUNT_IN_REPORT = getattr(
    settings,
    'ALDRYN_FORMS_PLUGINS_COUNT_IN_REPORT',
    10,
)


class PluginAdmin(admin.ModelAdmin):
    list_display = ['name', 'page_url', 'field_list']
    actions = None
    list_per_page = PLUGINS_COUNT_IN_REPORT
    list_max_show_all = 100
    prepopulated_fields = {'form_id': ('name',)}

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def page_url(self, obj):
        url = ''
        page = obj.placeholder.page
        if page:
            try:
                url = page.get_absolute_url()
            except:
                pass
        else:
            for o in obj.placeholder._get_attached_objects():
                if o:
                    try:
                        url = o.get_absolute_url()
                    except:
                        pass
                if url:
                    break
        if url:
            return format_html(
                '<a href="{}">{}</a>',
                url, url
            )
        return ''
    page_url.short_description = 'Page'

    def field_list(self, obj):
        text = format_html('')
        for field in obj.get_form_fields():
            text += format_html('{}, {}, {}<br>', field.label, field.name, field.plugin_instance.plugin_type)
        return text
    field_list.short_description = 'Fields'

#admin.site.register(EmailNotificationFormPlugin, PluginAdmin)
