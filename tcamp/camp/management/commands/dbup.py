import os
import sys
import datetime
import pexpect

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    args = '<sourcedb destdb>'
    help = '''Grabs a psql database (named in local settings) and
              loads it into another psql database (also named in local settings).
              '''

    def handle(self, *args, **options):
        if not len(args) is 2:
            sys.exit('Usage: ./manage.py dbup [sourcedb] [destdb]')
        sourcedb = settings.DATABASES[args[0]]
        destdb = settings.DATABASES[args[1]]
        dbauth = '-h %s -p %s -U %s -W %s'
        sourceauth = dbauth % (sourcedb['HOST'] or '127.0.0.1',
                               sourcedb['PORT'] or 5432,
                               sourcedb['USER'],
                               sourcedb['NAME'], )
        destauth = dbauth % (destdb['HOST'] or '127.0.0.1',
                             destdb['PORT'] or 5432,
                             destdb['USER'],
                             destdb['NAME'], )
        pwprompt = '[pP]assword.*:'
        timeout = 30
        ts = datetime.datetime.now().isoformat()
        temppath = '%s/.tmp' % settings.PROJECT_ROOT
        tempfile = '%s/%s_%s.sql' % (temppath, args[0], ts)
        try:
            os.mkdir(temppath)
        except OSError:
            if os.path.isdir(temppath):
                pass
            else:
                raise

        get_cmd = 'pg_dump -f %s %s' % (tempfile, sourceauth)
        get = pexpect.spawn(get_cmd)
        get.logfile_read = sys.stdout
        get.expect(pwprompt, timeout=timeout)
        get.sendline(sourcedb['PASSWORD'])
        get.expect(pexpect.EOF)

        drop_cmd = 'dropdb %s' % destauth
        drop = pexpect.spawn(drop_cmd)
        drop.logfile_read = sys.stdout
        drop.expect(pwprompt, timeout=timeout)
        drop.sendline(destdb['PASSWORD'])
        drop.expect(pexpect.EOF)

        create_cmd = 'createdb %s' % destauth
        create = pexpect.spawn(create_cmd)
        create.logfile_read = sys.stdout
        create.expect(pwprompt, timeout=timeout)
        create.sendline(destdb['PASSWORD'])
        create.expect(pexpect.EOF)

        put_cmd = 'psql -f %s %s' % (tempfile, destauth, )
        put = pexpect.spawn(put_cmd)
        put.logfile_read = sys.stdout
        put.expect(pwprompt, timeout=timeout)
        put.sendline(destdb['PASSWORD'])
        put.expect(pexpect.EOF)

        print '%s copied to %s.' % (args[0], args[1])
        os.remove(tempfile)
        try:
            os.rmdir(temppath)
        except:
            pass
