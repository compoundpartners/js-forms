# -*- coding: utf-8 -*-
from collections import defaultdict

from django.contrib import admin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext
# we use SortedDict to remain compatible across python versions
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext, ugettext_lazy as _

from django_tablib.views import export

from .forms import FormExportForm
from .models import FormData


class FormDataAdmin(admin.ModelAdmin):

    date_hierarchy = 'sent_at'
    list_display = ['__unicode__', 'sent_at']
    list_filter = ['name', 'people_notified']
    model = FormData
    readonly_fields = ['name', 'data', 'language', 'sent_at', 'people_notified']

    def get_urls(self):
        from django.conf.urls import patterns, url

        info = "%s_%s" % (self.model._meta.app_label, self.model._meta.module_name)

        def pattern(regex, fn, name):
            args = [regex, self.admin_site.admin_view(fn)]
            return url(*args, name='%s_%s' % (info, name))

        url_patterns = patterns('',
            pattern(r'export/$', self.form_export, 'export'),
        )

        return url_patterns + super(FormDataAdmin, self).get_urls()

    def form_export(self, request):
        opts = self.model._meta
        app_label = opts.app_label
        context = RequestContext(request)
        form = FormExportForm(request.POST or None)

        if form.is_valid():
            entries = form.get_queryset()

            if entries.exists():
                filename = form.get_filename()

                # A user can add fields to the form over time,
                # knowing this we use the latest form submission as a way
                # to get the latest form state, but this means that if a field
                # was removed then it will be ignored :(
                first_entry = entries.order_by('-sent_at')[0]

                # what follows is a bit of dark magic...
                # we call the export view in tablib with a headers dictionary, this dictionary
                # maps a key to a callable that gets passed a form submission instance and returns the value
                # for the field, we have to use a factory function in order to avoid a closure

                def clean_data(label, position):
                    def _clean_data(obj):
                        field = None
                        value = ''

                        try:
                            field = obj.get_data()[position]
                        except IndexError:
                            pass

                        if field and field.label == label:
                            # sanity check
                            # we need this to make sure that the field label and position remain constant
                            # otherwise we'll confuse users if a field was moved.
                            value = field.value
                        return value
                    return _clean_data

                fields = first_entry.get_data()

                # used to keep track of occurrences
                # in case a field with the same name appears multiple times in the form.
                occurrences = defaultdict(lambda: 1)
                headers = SortedDict()

                for position, field in enumerate(fields):
                    label = field.label

                    if label in headers:
                        occurrences[label] += 1
                        label = u'%s %s' % (label, occurrences[label])
                    headers[label] = clean_data(field.label, position)

                headers[ugettext('Language')] = 'language'
                headers[ugettext('Submitted on')] = 'sent_at'

                response = export(
                    request,
                    queryset=entries,
                    model=entries.model,
                    headers=headers,
                    format='xls', # we can make this a field in the form ;)
                    filename=filename
                )
                return response
            else:
                self.message_user(request, _("No records found"), level=messages.WARNING)
                return redirect('admin:aldryn_forms_formdata_export')
        else:
            context['errors'] = form.errors

        context.update({
            'adminform': form,
            'media': self.media + form.media,
            'has_change_permission': True,
            'opts': opts,
            'root_path': reverse('admin:index'),
            'current_app': self.admin_site.name,
            'app_label': app_label,
            'original': 'Export',
        })
        return render_to_response('admin/aldryn_forms/export.html', context)

admin.site.register(FormData, FormDataAdmin)
