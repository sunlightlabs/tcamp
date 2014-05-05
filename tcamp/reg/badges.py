import qrcode
from qrcode.image.svg import *
from django.core.exceptions import PermissionDenied
import shortuuid, uuid
from cStringIO import StringIO
from django.http import HttpResponse
from sked.urls import CURRENT_EVENT
from reg.models import Ticket, CouponCode
from reg.reports import get_staff_domains
import json, csv
import math

### caching and auth
from django.core.cache import cache as _djcache
def cache(seconds = 900):
    def doCache(f):
        def x(*args, **kwargs):
                key = sha1(str(f.__module__) + str(f.__name__) + str(args) + str(kwargs)).hexdigest()
                result = _djcache.get(key)
                if result is None:
                    result = f(*args, **kwargs)
                    _djcache.set(key, result, seconds)
                return result
        return x
    return doCache

def key_is_staff(key):
    if not key:
        return False

    try:
        ukey = shortuuid.decode(key)
    except:
        return False

    ticket = list(Ticket.objects.filter(barcode=ukey).select_related())
    if not ticket:
        return False

    ticket = ticket[0]
    coupon = ticket.sale.coupon_code

    if coupon and coupon.is_staff:
        return True
    else:
        return False


def require_staff_code(func):
    def wrapped(request, *args, **kwargs):
        key = request.GET.get('key', '')
        if key_is_staff(key):
            return func(request, *args, **kwargs)
        else:
            raise PermissionDenied()
    return wrapped

## views

def qrcode_svg(request, barcode, format):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    qr.add_data(barcode)
    qr.make(fit=True)

    buff = StringIO()

    if format == 'svg':
        img = qr.make_image(SvgImage)
        img.save(buff)
        
        scale = 15.0 / img.width

        out = \
"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE svg>
<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'>
    <g transform="scale(%s,%s)">
        %s
    </g>
</svg>
""" % (scale, scale, buff.getvalue().replace("<?xml version='1.0' encoding='UTF-8'?>", ""))
        
        return HttpResponse(out, content_type="image/svg+xml")
    elif format == 'png':
        img = qr.make_image()
        img.save(buff)

        return HttpResponse(buff.getvalue(), content_type="image/png")

MAX_UUID = float(uuid.UUID('ffffffff-ffff-ffff-ffff-ffffffffffff').int)

@require_staff_code
def attendees(request, format):
    staff_domains = get_staff_domains()
    fdomains = ['@%s' % domain for domain in staff_domains] if staff_domains else []
    fcoupon = set([c.id for c in CouponCode.objects.filter(is_staff=True)])

    out = []
    for ticket in Ticket.objects.filter(success=True, event=CURRENT_EVENT).select_related():
        # are they staff?
        is_staff = True if (ticket.email and any([fdomain in ticket.email for fdomain in fdomains])) or \
            (ticket.sale.email and any([fdomain in ticket.sale.email for fdomain in fdomains])) or \
            (ticket.sale.coupon_code and ticket.sale.coupon_code.id in fcoupon) else False

        # prep their qr code
        qrcode_uuid = uuid.UUID(ticket.barcode)
        qrcode = shortuuid.encode(qrcode_uuid)
        out.append({
            'first_name': ticket.first_name,
            'last_name': ticket.last_name,
            'qrcode': qrcode,
            'qrcode_path': request.build_absolute_uri('/register/badges/qrcode/%s.png' % qrcode),
            'twitter': ticket.clean_twitter,
            'organization': ticket.organization,
            'is_staff': is_staff,
            'color': int(math.floor(10 * (qrcode_uuid.int / MAX_UUID)))
        })
    if format == 'json':
        return HttpResponse(json.dumps(out), content_type="application/json")
    elif format == 'csv':
        response = HttpResponse(content_type="text/csv")
        outc = csv.DictWriter(response, ['first_name', 'last_name', 'qrcode', 'qrcode_path', 'twitter', 'organization', 'is_staff', 'color'])
        outc.writeheader()
        
        for row in out:
            outc.writerow(
                dict([(key, value.encode('utf8') if type(value) == unicode else value) for key, value in row.items()])
            )

        return response