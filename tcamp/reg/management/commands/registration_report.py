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

        sales = {}
        stats = defaultdict(int)
        coupons = defaultdict(int)
        types = defaultdict(int)
        ambassador = defaultdict(int)
        type_labels = {}
        for ticket in query.order_by('id').select_related():
            sales[ticket.sale.id] = ticket.sale

            stats['tickets'] += 1
            if (ticket.email and fdomain and fdomain in ticket.email) or \
                (ticket.sale.email and fdomain and fdomain in ticket.sale.email) or \
                (ticket.sale.coupon_code and ticket.sale.coupon_code.id == fcoupon.id):
                    stats['staff'] += 1
            else:
                stats['non_staff'] += 1
                if ticket.sale.coupon_code:
                    stats['ns_coupon'] += 1
                    coupons[ticket.sale.coupon_code.code] += 1
                types[ticket.type.id] += 1
                type_labels[ticket.type.id] = ticket.type.name

            if ticket.lobby_day:
                stats['lobby_day'] += 1

            ambassador[ticket.ambassador_program] += 1



        print "Total tickets:", stats['tickets']
        print "  Staff:", stats['staff']
        print "  Non-staff:", stats['non_staff']
        print ""

        print "Non-staff tickets by type:"
        for i in sorted(types.keys()):
            print " ", type_labels[i] + ":", types[i]
        print ""
        print "Non-staff tickets purchased with coupons:", stats['ns_coupon']
        for c, num in coupons.items():
            print " ", c + ":", num
        print ""
        print "Lobby day participants:", stats['lobby_day']
        print ""
        print "Ambassador program:"
        for key, label in AMBASSADOR_PROGRAM_CHOICES:
            print " ", label + ":", ambassador[key]
        print ""
        print "Total sales:", sum([float(sale.amount) for sale in sales.values()])