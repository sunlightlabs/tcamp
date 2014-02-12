from django.core.management.base import BaseCommand, CommandError
from reg.models import *

from optparse import make_option
import cStringIO, csv

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    option_list = BaseCommand.option_list + (
        make_option('--exclude-domain',
            action='store',
            dest='exclude_domain',
            default=None,
            help='Exclude tickets with email addresses from this domain'),
        make_option('--exclude-coupon',
            action='store',
            dest='exclude_coupon',
            default=None,
            help='Exclude tickets that used this coupon'),
        make_option('--output',
            action='store',
            dest='output',
            default=None,
            help='Output CSV to a file'),
    )

    def handle(self, *args, **options):
        FIELDS = ["Prefix", "Middle", "Suffix", "Firstname", "Lastname", "Mailname", "Address1", "Address2", "Address3", "City", "State", "Zip", "Carrier_rt", "Salutation", "Employer", "Occupation", "Organization", "WorkPhone", "WorkExtension", "FaxPhone", "Email", "HomePhone", "Phone3", "Phone4", "Phone5", "County", "Precinct", "Gender", "Congress", "Statesenate", "Statehouse", "Districta", "Districtb", "Districtc", "Party", "Spousename", "Notes", "User1", "User2", "User3", "User4", "User5", "User6", "PACname", "CmteID", "AskToGive", "AskToRaise", "WebSite", "Email2", "Industry", "CandState", "CandID", "CandCycle", "CandDistrict", "CandOffice", "Assistant", "Nickname", "Birthdate", "Candname", "Work", "Mailname", "Work", "Address1", "Work", "Address2", "Work", "Address3", "Work", "City", "Work", "State", "Work", "Zip", "contrib_Date", "contrib_Amount", "contrib_Note", "contrib_Check", "contrib_Deposit", "contrib_Account", "contrib_Period", "contrib_Cycle", "contrib_Member", "contrib_Method", "contrib_Source", "contrib_Attribution", "contrib_ReportCode1", "contrib_Link", "contrib_Attribution2", "contrib_Batch", "contrib_ThankYou", "Twitter", "Subscribe"]
        from reg.views import CURRENT_EVENT

        search = {
            'success': True,
            'event': CURRENT_EVENT
        }
        exclude = {}
        if options['exclude_coupon']:
            coupon = CouponCode.objects.get(code=options['exclude_coupon'])
            exclude['coupon_code'] = coupon

        query = Sale.objects.filter(**search)
        if exclude:
            query = query.exclude(**exclude)

        fdomain = '@%s' % options['exclude_domain'] if options['exclude_domain'] else None

        outs = cStringIO.StringIO()
        outc = csv.DictWriter(outs, FIELDS)
        outc.writeheader()

        for sale in query.order_by('id').select_related():
            tickets = list(sale.ticket_set.all())
            if len(tickets) == 0:
                continue

            tk = []
            sale_used = False
            for ticket in tickets:
                if ticket.last_name == sale.last_name and ticket.email == sale.email:
                    # pair them together
                    tk.append({'sale': sale, 'ticket': ticket})
                    sale_used = True
                else:
                    tk.append({'sale': Sale(), 'ticket': ticket})
            if not sale_used and sale.last_name:
                tk.append({'sale': sale, 'ticket': Ticket()})

            for record in tk:
                s = record['sale']
                t = record['ticket']

                if fdomain and (fdomain in s.email or fdomain in t.email):
                    continue

                record = {
                    'Firstname': (t.first_name or s.first_name).encode('utf8'),
                    'Lastname': (t.last_name or s.last_name).encode('utf8'),
                    'Mailname': ' '.join((s.first_name, s.last_name)).strip(),
                    'Address1': s.address1.encode('utf8'),
                    'Address2': s.address2.encode('utf8'),
                    'City': s.city.encode('utf8'),
                    'State': s.state.encode('utf8'),
                    'Zip': s.zip,
                    'Employer': t.organization.encode('utf8'),
                    'Organization': t.organization.encode('utf8'),
                    'Occupation': t.title.encode('utf8'),
                    'WebSite': t.website if ('://' in t.website or not t.website) else 'http://%s' % t.website,
                    'Email': t.email or s.email,
                    'Twitter': t.clean_twitter,
                    'Subscribe': 'Y' if t.subscribe else 'N'

                }
                print s.id or "-", t.id or "-"
                print record
                outc.writerow(record)

        if options['output']:
            f = open(options['output'], 'wb')
            f.write(outs.getvalue())
            f.close()
        else:
            print outs.getvalue()