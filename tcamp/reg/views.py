from django.shortcuts import render_to_response
from reg.models import *
from reg.forms import *

from sked.urls import CURRENT_EVENT

def register(request):
    sale_form = SaleForm()
    ticket_form = TicketForm()

    ticket_types = TicketType.objects.all(event=CURRENT_EVENT, enabled=True).order_by('position')

    return render_to_response('reg/register.html', {'ticket_form': ticket_form, 'sale_form': sale_form, 'ticket_types': ticket_types}, context_instance=RequestContext(request))