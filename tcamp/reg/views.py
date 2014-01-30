from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from reg.models import *
from reg.forms import *

from django.http import Http404, HttpResponse

from sked.urls import CURRENT_EVENT

import json

def register(request):
    sale_form = SaleForm()
    ticket_form = TicketForm()

    ticket_types = TicketType.objects.filter(event=CURRENT_EVENT, enabled=True).order_by('position')

    return render_to_response('reg/register.html', {'ticket_form': ticket_form, 'sale_form': sale_form, 'ticket_types': ticket_types}, context_instance=RequestContext(request))

@csrf_exempt
def price_check(request):
    if request.method != "POST":
        raise Http404
    try:
        data = json.loads(request.raw_post_data)
    except:
        raise Http404

    return HttpResponse(json.dumps(get_price_data(tickets=data['tickets'], coupon=data.get('coupon', None))))

# utilities
def get_price_data(tickets={}, coupon=None):
    out = {}
    total = 0
    for tk, qty in tickets.items():
        ticket = TicketType.objects.get(id=tk)
        total += float(ticket.price) * qty

    if coupon:
        try:
            cp = CouponCode.objects.get(event=CURRENT_EVENT, code=coupon)
            out['coupon'] = coupon
            total -= (cp.discount / 100.0) * total
        except:
            out['coupon_error'] = "Coupon code not found."
    out['price'] = total

    return out
