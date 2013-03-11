from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

template_path_regex = r'^[-a-zA-Z0-9:_\./\\]+$'
validate_template_path = RegexValidator(template_path_regex, _("Enter a valid 'template path' consisting of letters, numbers, underscores, hyphens, forward or backslashes, periods and/or colons."), 'invalid')
