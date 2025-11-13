# -*- coding: utf-8 -*-
from django.urls import reverse, resolve
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from cms.utils.page import get_page_from_request

from .models import FormPlugin

@csrf_exempt
def submit_form_view(request):
    cms_page = get_page_from_request(request)

    if not cms_page:
        return HttpResponseBadRequest()

    template = cms_page.get_template()

    context = {
        'current_app': resolve(request.path).namespace,
        'current_page': cms_page,
    }

    if request.method == 'POST':
        form_plugin_id = request.POST.get('form_plugin_id') or ''

        if not form_plugin_id.isdigit():
            # fail if plugin_id has been tampered with
            return HttpResponseBadRequest()

        try:
            # I believe this could be an issue as we don't check if the form submitted
            # is in anyway tied to this page.
            # But then we have a problem with static placeholders :(
            form_plugin = FormPlugin.objects.get(pk=form_plugin_id)
        except FormPlugin.DoesNotExist:
            return HttpResponseBadRequest()

        form_plugin_instance = form_plugin.get_plugin_instance()[1]
        # saves the form if it's valid
        form = form_plugin_instance.process_form(form_plugin, request)
        success_url = form_plugin_instance.get_success_url(instance=form_plugin)

        if form.is_valid() and success_url:
            return HttpResponseRedirect(success_url)
        if form_plugin.form_template:
            template = form_plugin.form_template
            if not template.startswith('aldryn_forms/'):
                template = 'aldryn_forms/' + template
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
            parts = template.split('/')
            parts.insert(-1, 'ajax')
            template = '/'.join(parts)


        context['post_success'] = True
        context['form_success_url'] = success_url
        context['post_request'] = True
        context['form'] = form
        
    return render(request, template, context)

@csrf_protect
def submit_form_view_protect(request):
    return submit_form_view(request)
