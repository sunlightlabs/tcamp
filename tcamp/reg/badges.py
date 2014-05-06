import qrcode
from qrcode.image.svg import *
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import never_cache
import shortuuid, uuid
from cStringIO import StringIO
from django.http import HttpResponse
from sked.urls import CURRENT_EVENT
from reg.models import Ticket, CouponCode
from reg.reports import get_staff_domains
import json, csv, zipfile
import math

### caching and auth
# taken from http://djangosnippets.org/snippets/564/
from django.core.cache import cache as _djcache
from hashlib import sha1
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

@cache(seconds=900)
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

## QR code stuff

def qrcode_image(request, barcode, format):
    img_data = get_qrcode_image(barcode, format)
    mimes = {'svg': 'image/svg+xml', 'png': 'image/png'}
    return HttpResponse(img_data, mimes[format])

def get_qrcode_image(barcode, format):
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
        
        return out
    elif format == 'png':
        img = qr.make_image()
        img.save(buff)

        return buff.getvalue()

## data export stuff

MAX_UUID = float(uuid.UUID('ffffffff-ffff-ffff-ffff-ffffffffffff').int)
ICON_NAMES = ['bear.eps', 'bird.eps', 'canoe.eps', 'fire.eps', 'fish.eps', 'ivy.eps', 'robot.eps', 'sun.eps', 'tent.eps', 'tree.eps']

@never_cache
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
            'qrcode_png': '%s.png' % qrcode if format == 'zip' else request.build_absolute_uri('/register/badges/qrcode/%s.png' % qrcode),
            'qrcode_svg': '%s.svg' % qrcode if format == 'zip' else request.build_absolute_uri('/register/badges/qrcode/%s.svg' % qrcode),
            'twitter': ticket.clean_twitter,
            'organization': ticket.organization,
            'is_staff': is_staff,
            'icon': ICON_NAMES[int(math.floor(10 * (qrcode_uuid.int / MAX_UUID)))]
        })
    if format == 'json':
        return HttpResponse(json.dumps(out), content_type="application/json")
    elif format in ('csv', 'zip'):
        csvbuff = StringIO()        
        outc = csv.DictWriter(csvbuff, ['first_name', 'last_name', 'qrcode', 'qrcode_png', 'qrcode_svg', 'twitter', 'organization', 'is_staff', 'icon'])
        outc.writeheader()
        
        for row in out:
            outc.writerow(
                dict([(key, value.encode('utf8') if type(value) == unicode else value) for key, value in row.items()])
            )

        if format == 'csv':
            return HttpResponse(csvbuff.getvalue(), content_type="text/csv")
        elif format == 'zip':
            zipbuff = StringIO()
            outz = zipfile.ZipFile(zipbuff, 'w', zipfile.ZIP_DEFLATED)

            outz.writestr('export.csv', csvbuff.getvalue())
            for row in out:
                outz.writestr(row['qrcode_png'], get_qrcode_image(row['qrcode'], 'png'), zipfile.ZIP_STORED)
                outz.writestr(row['qrcode_svg'], get_qrcode_image(row['qrcode'], 'svg'))

            outz.close()

            return HttpResponse(zipbuff.getvalue(), content_type="application/zip")