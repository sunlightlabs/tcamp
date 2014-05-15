import qrcode
from qrcode.image.svg import *
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import never_cache
import shortuuid, uuid
from cStringIO import StringIO
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from dateutil import parser
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

    out_data = {}
    if format in ('svg', 'both'):
        buff = StringIO()

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
        
        if format == 'svg':
            return out
        else:
            out_data['svg'] = out
    if format in ('png', 'both'):
        buff = StringIO()

        img = qr.make_image()
        img.save(buff)

        if format == 'png':
            return buff.getvalue()
        else:
            out_data['png'] = buff.getvalue()

    return out_data

## data export stuff

MAX_UUID = float(uuid.UUID('ffffffff-ffff-ffff-ffff-ffffffffffff').int)
ICON_NAMES = ['bear.eps', 'bird.eps', 'canoe.eps', 'fire.eps', 'fish.eps', 'ivy.eps', 'robot.eps', 'sun.eps', 'tent.eps', 'tree.eps']

STAFF_INFO = {}
def get_badge(ticket, prefix='', compact=True):
    # prime the staff info dict
    if not STAFF_INFO:
        staff_domains = get_staff_domains()
        STAFF_INFO['domains'] = ['@%s' % domain for domain in staff_domains] if staff_domains else []
        STAFF_INFO['coupons'] = set([c.id for c in CouponCode.objects.filter(is_staff=True)])

    # are they staff?
    is_staff = True if (ticket.email and any([fdomain in ticket.email for fdomain in STAFF_INFO['domains']])) or \
        (ticket.sale.email and any([fdomain in ticket.sale.email for fdomain in STAFF_INFO['domains']])) or \
        (ticket.sale.coupon_code and ticket.sale.coupon_code.id in STAFF_INFO['coupons']) else False

    # prep their qr code
    qrcode_uuid = uuid.UUID(ticket.barcode)
    qrcode = shortuuid.encode(qrcode_uuid)
    out = {
        'first_name': ticket.first_name,
        'last_name': ticket.last_name,
        'qrcode': qrcode,
        'qrcode_png': '%s%s.png' % (prefix, qrcode),
        'qrcode_svg': '%s%s.svg' % (prefix, qrcode),
        'email': ticket.email,
        'twitter': ticket.clean_twitter,
        'organization': ticket.organization,
        'is_staff': is_staff,
        'icon': ICON_NAMES[int(math.floor(10 * (qrcode_uuid.int / MAX_UUID)))],
        'checked_in': ticket.checked_in.isoformat() if ticket.checked_in else None,
    }
    if not compact:
        out['title'] = ticket.title
        out['website'] = ticket.website
        out['diet'] = {
            'vegetarian': ticket.diet_vegetarian,
            'vegan': ticket.diet_vegan,
            'gluten_free': ticket.diet_gluten_free,
            'allergies': ticket.diet_allergies,
            'other': ticket.diet_other,
            'desc': {}
        }
        if out['diet']['allergies']:
            out['diet']['desc']['allergies'] = ticket.diet_allergies_desc
        if out['diet']['other']:
            out['diet']['desc']['other'] = ticket.diet_other_desc

        out['ambassador_program'] = ticket.ambassador_program
        out['lobby_day'] = ticket.lobby_day
        out['days'] = {'day1': ticket.attend_day1, 'day2': ticket.attend_day2}
    return out

def get_attendees(request, format):
    staff_domains = get_staff_domains()
    fdomains = ['@%s' % domain for domain in staff_domains] if staff_domains else []
    fcoupon = set([c.id for c in CouponCode.objects.filter(is_staff=True)])

    out = []
    prefix = '' if (format == 'zip' or not request) else request.build_absolute_uri('/register/badges/qrcode/')
    compact = format != 'json'
    for ticket in Ticket.objects.filter(success=True, event=CURRENT_EVENT).select_related():
        out.append(get_badge(ticket, prefix, compact))

    if format == 'json':
        return HttpResponse(json.dumps({'attendees': out}), content_type="application/json")
    elif format in ('csv', 'zip'):
        csvbuff = StringIO()        
        outc = csv.DictWriter(csvbuff, ['first_name', 'last_name', 'qrcode', 'qrcode_png', 'qrcode_svg', 'email', 'twitter', 'organization', 'is_staff', 'icon', 'checked_in'])
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
                img_data = get_qrcode_image(row['qrcode'], 'both')
                outz.writestr(row['qrcode_png'], img_data['png'], zipfile.ZIP_STORED)
                outz.writestr(row['qrcode_svg'], img_data['svg'])

            outz.close()

            return HttpResponse(zipbuff.getvalue(), content_type="application/zip")

attendees = never_cache(require_staff_code(get_attendees))

@never_cache
@require_staff_code
def attendee(request, barcode):
    prefix = request.build_absolute_uri('/register/badges/qrcode/')
    qrcode = shortuuid.decode(barcode)
    ticket = get_object_or_404(Ticket, barcode=qrcode, success=True)

    if request.method == "POST":
        checked_in = request.POST.get('checked_in', None)
        checked_in_bool = checked_in in (True, "true", "True", 1, "1", False, None, "False", "false", "null", 0)
        p_checked_in = None
        if checked_in and type(checked_in) in (str, unicode):
            try:
                p_checked_in = parser.parse(checked_in)
            except (AttributeError, ValueError):
                pass

        if 'checked_in' not in request.POST or (type(checked_in) in (str, unicode) and not p_checked_in and not checked_in_bool):
            return HttpResponseBadRequest(json.dumps({'error': 'checked_in parameter required, and must be a datetime, true, false, or null.'}), content_type="application/json")

        if checked_in in (False, None, "False", "false", "null", 0):
            ticket.checked_in = None
        else:
            if ticket.checked_in is not None:
                return HttpResponse(json.dumps({'error': 'Already checked in.'}), status=409, content_type="application/json")

            if checked_in in (True, "true", "True", 1, "1"):
                ticket.checked_in = timezone.localtime(timezone.now())
            elif p_checked_in:
                if not p_checked_in.tzinfo:
                    p_checked_in = p_checked_in.replace(tzinfo=timezone.get_current_timezone())
                ticket.checked_in = p_checked_in
        ticket.save()

    return HttpResponse(json.dumps(get_badge(ticket, prefix=prefix, compact=False)), content_type="application/json")
