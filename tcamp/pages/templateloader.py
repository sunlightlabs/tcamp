"""
Wrapper for loading templates from a database table.
"""

from django.template.base import Template, TemplateDoesNotExist
from django.template.loader import BaseLoader, get_template, get_template_from_string

from pages.models import Template as PageTemplate


class Loader(BaseLoader):
    is_usable = True

    def load_template(self, template_name, template_dirs=None):
        if isinstance(template_name, Template):
            return (template_name, '')
        # require that templates loaded via this loader start with 'pages:'
        if not template_name.startswith('pages:'):
            raise TemplateDoesNotExist(template_name)

        db_template_name = template_name.replace('pages:', '', 1)
        try:
            template = PageTemplate.objects.get(name__exact=db_template_name)
        except PageTemplate.DoesNotExist:
            raise TemplateDoesNotExist(template_name)

        if template.is_path:
            template = get_template(template.path)
        else:
            template = get_template_from_string(template.content)

        return (template, template_name)

_loader = Loader()
