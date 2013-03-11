import re
import json
import sys
import StringIO

from django.core.management.base import BaseCommand

import local_settings


class Command(BaseCommand):
    help = '''Serializes individual settings items into json-safe
              strings suitable for dumping into a .env for Foreman.'''

    VALID_SETTING = re.compile(r'^[A-Z0-9_]+$')

    def handle(self, *args, **options):
        flo = StringIO.StringIO()
        failed_settings = []
        settings_d = local_settings.__dict__
        for setting, value in settings_d.iteritems():
            if not self.VALID_SETTING.search(setting):
                continue

            if setting == u"DATABASES":
                continue

            try:
                flo.write(u"%s=%s\n" % (setting, json.dumps(value)))
            except Exception, e:
                failed_settings.append("%s: %s" % (setting, e))

        flo.seek(0)
        sys.stdout.writelines(flo.readlines())
        if len(failed_settings):
            sys.stderr.write('Failed to parse some settings:\n')
            sys.stderr.write('\n'.join(failed_settings))
