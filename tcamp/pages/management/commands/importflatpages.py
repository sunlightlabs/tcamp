from django.core.management.base import BaseCommand
from django.contrib.flatpages.models import FlatPage

from pages.models import Page, Template


class Command(BaseCommand):
    help = 'Copies Flatpage content into new Page objects'

    def handle(self, *args, **options):

        for fp in FlatPage.objects.all():

            try:

                p = Page.objects.get(path=fp.url)

                print "%s already exists" % fp.url

            except Page.DoesNotExist:

                p = Page()

                p.path = fp.url
                p.title = fp.title
                p.content = fp.content
                p.content.markup_type = 'markdown'

                p.template = self.get_template(fp.template_name)
                p.is_published = True

                p.save()

                print "saved %s" % fp.url

    def get_template(self, path):

        if not path:
            path = 'flatpages/default.html'

        try:
            t = Template.objects.get(content=path)
        except Template.DoesNotExist:
            t = Template.objects.create(name='unknown', content=path, is_path=True)

        return t
