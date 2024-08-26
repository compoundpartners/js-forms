# -*- coding: utf-8 -*-
import re
from email.utils import parseaddr

from django.core.exceptions import ValidationError
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    validate_email,
    RegexValidator,
    _lazy_re_compile,
)
from django.utils.translation import gettext_lazy as _


def is_valid_recipient(recipient):
    """
    recipient - a string in any of the following formats (RFC 2822):
        name
        useremail@gmail.com
        name <useremail@mail.com>
    """
    if not recipient:
        return False

    email_address = parseaddr(recipient)[1]

    try:
        validate_email(email_address)
    except ValidationError:
        return False
    else:
        return True


class MinChoicesValidator(MinLengthValidator):

    message = _('You have to choose at least %(limit_value)d options (chosen %(show_value)d).')
    code = 'min_choices'


class MaxChoicesValidator(MaxLengthValidator):

    message = _('You can\'t choose more than %(limit_value)d options (chosen %(show_value)d).')
    code = 'max_choices'

alphabet_re = _lazy_re_compile(r'^[ \w\-\']+\Z', re.UNICODE)
validate_alphabet = RegexValidator(
    alphabet_re,
    _("Field can only contain letters of the alphabet."),
    'invalid'
)

