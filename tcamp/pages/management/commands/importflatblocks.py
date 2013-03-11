from django.core.management.base import BaseCommand
from flatblocks.models import FlatBlock

from pages.models import Chunk


class Command(BaseCommand):
    help = 'Copes FlatBlock content into new Chunk objects'

    def handle(self, *args, **options):

        for fb in FlatBlock.objects.all():

            try:

                c = Chunk.objects.get(slug=fb.slug)

                print "%s already exists" % fb.slug

            except Chunk.DoesNotExist:

                c = Chunk()

                c.slug = fb.slug
                c.content = fb.content
                c.content.markup_type = 'markdown'

                c.save()

                print "saved %s" % fb.slug
