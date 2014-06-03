from django.conf import settings
from reg.models import *
from collections import defaultdict
import datetime
import csv
from cStringIO import StringIO

def get_staff_domains():
    staff_domains = set()
    for admin in settings.ADMINS:
        staff_domains.add(admin[1].split('@')[1])
    return list(staff_domains)

def get_registration_report():
    from reg.views import CURRENT_EVENT

    search = {
        'success': True,
        'event': CURRENT_EVENT
    }

    query = Ticket.objects.filter(**search)

    staff_domains = get_staff_domains()
    fdomains = ['@%s' % domain for domain in staff_domains] if staff_domains else []
    fcoupon = set([c.id for c in CouponCode.objects.filter(is_staff=True)])

    sales = {}
    stats = defaultdict(int)
    coupons = defaultdict(int)
    types = defaultdict(int)
    ambassador = defaultdict(int)
    type_labels = {}
    for ticket in query.order_by('id').select_related():
        sales[ticket.sale.id] = ticket.sale

        stats['tickets'] += 1
        if (ticket.email and any([fdomain in ticket.email for fdomain in fdomains])) or \
            (ticket.sale.coupon_code and ticket.sale.coupon_code.id in fcoupon):
                stats['staff'] += 1
        else:
            stats['non_staff'] += 1
            types[ticket.type.id] += 1
            type_labels[ticket.type.id] = ticket.type.name

        if ticket.sale.coupon_code and not ticket.sale.coupon_code.is_staff:
            stats['ns_coupon'] += 1
            coupons[ticket.sale.coupon_code.code] += 1

        if ticket.lobby_day:
            stats['lobby_day'] += 1

        ambassador[ticket.ambassador_program] += 1


    return {
        'stats': stats,
        'type_breakdown': [(type_labels[i], types[i]) for i in sorted(types.keys())],
        'ambassador_counts': [(label, ambassador[key]) for key, label in AMBASSADOR_PROGRAM_CHOICES],
        'total_sales': sum([float(sale.amount) for sale in sales.values()]),
        'coupons': dict(coupons)
    }

def get_volunteer_export():
    outfile = StringIO()
    outcsv = csv.DictWriter(outfile, ['ticket_id', 'first_name', 'last_name', 'organization', 'email', 'checked_in'])
    outcsv.writeheader()

    from reg.views import CURRENT_EVENT
    for ticket in Ticket.objects.filter(event=CURRENT_EVENT, sale__success=True, type__name__contains="Volunteer").order_by('id').select_related():
        outcsv.writerow({'ticket_id': ticket.id, 'first_name': ticket.first_name, 'last_name': ticket.last_name, 'organization': ticket.organization, 'email': ticket.email, 'checked_in': "Y" if ticket.checked_in else "N"})

    return outfile.getvalue()

def get_attendee_export():
    outfile = StringIO()
    outcsv = csv.DictWriter(outfile, ['ticket_id', 'first_name', 'last_name', 'organization', 'email', 'ticket_type', 'ambassador', 'checked_in'])
    outcsv.writeheader()
    ambassador_choices = dict(AMBASSADOR_PROGRAM_CHOICES)

    from reg.views import CURRENT_EVENT
    for ticket in Ticket.objects.filter(event=CURRENT_EVENT, sale__success=True).order_by('id').select_related():
        outcsv.writerow({'ticket_id': ticket.id, 'first_name': ticket.first_name.encode('utf8'), 'last_name': ticket.last_name.encode('utf8'), 'organization': ticket.organization.encode('utf8'), 'email': ticket.email, 'ticket_type': ticket.type.name, 'ambassador': ambassador_choices[ticket.ambassador_program], 'checked_in': "Y" if ticket.checked_in else "N"})

    return outfile.getvalue()