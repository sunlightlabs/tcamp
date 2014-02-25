from django.core.management.base import BaseCommand, CommandError
from reg.models import *

from optparse import make_option
import cStringIO, csv
from collections import defaultdict

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    option_list = BaseCommand.option_list + (
        make_option('--staff-domain',
            action='store',
            dest='staff_domain',
            default=None,
            help='Exclude tickets with email addresses from this domain'),
        make_option('--staff-coupon',
            action='store',
            dest='staff_coupon',
            default=None,
            help='Exclude tickets that used this coupon'),
        make_option('--output',
            action='store',
            dest='output',
            default=None,
            help='Output CSV to a file'),
    )

    def handle(self, *args, **options):
        from reg.views import CURRENT_EVENT

        search = {
            'success': True,
            'event': CURRENT_EVENT
        }

        query = Ticket.objects.filter(**search)

        fdomain = '@%s' % options['staff_domain'] if options['staff_domain'] else None
        fcoupon = CouponCode.objects.get(code=options['staff_coupon']) if options['staff_coupon'] else CouponCode()

        outs = cStringIO.StringIO()
        outc = csv.DictWriter(outs, ['first_name', 'last_name', 'email', 'state', 'organization', 'ticket_type', 'is_staff'])
        outc.writeheader()

        for ticket in query.order_by('id').select_related():
            if ticket.lobby_day:
                staff = (ticket.email and fdomain and fdomain in ticket.email) or \
                    (ticket.sale.email and fdomain and fdomain in ticket.sale.email) or \
                    (ticket.sale.coupon_code and ticket.sale.coupon_code.id == fcoupon.id)

                outc.writerow({
                    'first_name': ticket.first_name.encode('utf8'),
                    'last_name': ticket.last_name.encode('utf8'),
                    'email': ticket.email.encode('utf8'),
                    'state': ticket.sale.state.encode('utf8'),
                    'organization': ticket.organization.encode('utf8'),
                    'ticket_type': ticket.type.name,
                    'is_staff': 'Y' if staff else 'N',
                })

        if options['output']:
            f = open(options['output'], 'wb')
            f.write(outs.getvalue())
            f.close()
        else:
            print outs.getvalue()