from aldryn_client import forms

ACTIONS = (
    ('email_only', 'Email only'),
    ('default', 'Email and Save'),
    ('none', 'None'),
)


class Form(forms.BaseForm):

    show_all_recipients = forms.CheckboxField('Show all users as selectable e-mail recipients (not only admins)', required=False, initial=True)
    enable_simple_forms = forms.CheckboxField('Enable Simple forms', required=False, initial=False)
    enable_form_template = forms.CheckboxField('Enable Form template', required=False, initial=False)
    enable_custom_css = forms.CheckboxField('Enable Custom CSS classes', required=False, initial=False)
    enable_localstorage = forms.CheckboxField('Enable local storage', required=False, initial=False)
    enable_api = forms.CheckboxField('Enable API options', required=False, initial=False)
    enable_form_id = forms.CheckboxField('Enable Form ID', required=False, initial=False)
    default_action_backend = forms.SelectField('Default Action', ACTIONS, required=True)
    recaptcha_private_key = forms.CharField('ReCaptcha Private Key', required=False)
    recaptcha_public_key = forms.CharField('ReCaptcha Public Key', required=False)
    recaptcha_use_v3 = forms.CharField('Use ReCaptcha v3', required=False)


    def to_settings(self, data, settings):
        settings['ALDRYN_FORMS_ENABLE_API'] = True
        settings['ALDRYN_FORMS_SHOW_ALL_RECIPIENTS'] = data['show_all_recipients']
        settings['ALDRYN_FORMS_ENABLE_LOCALSTORAGE'] = data['enable_localstorage']
        settings['ALDRYN_FORMS_ENABLE_SIMPLE_FORMS'] = data['enable_simple_forms']
        settings['ALDRYN_FORMS_ENABLE_FORM_TEMPLATE'] = data['enable_form_template']
        settings['ALDRYN_FORMS_ENABLE_CUSTOM_CSS'] = data['enable_custom_css']
        settings['ALDRYN_FORMS_DEFAULT_ACTION_BACKEND'] = data['default_action_backend']
        settings['ALDRYN_FORMS_ENABLE_API'] = data['enable_api']
        settings['ALDRYN_FORMS_ENABLE_FORM_ID'] = data['enable_form_id']
        if data['recaptcha_private_key']:
            settings['RECAPTCHA_PRIVATE_KEY'] = data['recaptcha_private_key']
        if data['recaptcha_public_key']:
            settings['RECAPTCHA_PUBLIC_KEY'] = data['recaptcha_public_key']
        if data['recaptcha_use_v3']:
            settings['RECAPTCHA_USE_V3'] = data['recaptcha_use_v3']
            settings['RECAPTCHA_SCORE_THRESHOLD'] = 0.5
            settings['RECAPTCHA_DEFAULT_ACTION'] = 'generic'
            settings['INSTALLED_APPS'].append('snowpenguin.django.recaptcha3')
        else:
            settings['INSTALLED_APPS'].append('snowpenguin.django.recaptcha2')
        return settings
