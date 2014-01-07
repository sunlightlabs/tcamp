import urlparse

from django.core.urlresolvers import resolve
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView
from camp.models import EmailSubscriber
from camp.forms import BootstrapErrorList
from sked.models import Event


def index(request):
    pass


def login(request):
    referer = request.META.get('HTTP_REFERER')
    try:
        path = urlparse.urlparse(referer).path
    except:
        path = None

    if referer and urlparse.urlparse(referer).netloc == request.META.get('HTTP_HOST'):
        try:
            resolve(path)
        except:
            path = None
    else:
        path = None

    if request.user.is_anonymous():
        if path:
            request.session['next'] = path
        else:
            request.session['next'] = '/'
        return render(request, 'public_login.html')
    else:
        return redirect('/logged-in/')


def logged_in(request):
    if request.user.is_staff and not request.session.get('next'):
        return redirect('/admin/')
    else:
        try:
            del request.session['next']
        except:
            pass
        return redirect(request.session.get('next', '/'))


@require_POST
def sponsor_contact(request):
    pass


@require_POST
@never_cache
def email_subscribe(request):
    email = request.POST.get('email')
    event = Event.objects.current()
    subscriber = None
    if email and event:
        try:
            subscriber = EmailSubscriber.objects.get_or_create(event_id=event.id, email=email)
            template = 'camp/partials/success.html'
            error = None
        except:
            template = 'camp/partials/email_subscriber_form.html'
            error = 'There was an error subscribing you.'
    else:
        template = 'camp/partials/email_subscriber_form.html'
        error = 'Please provide an email address.'

    return render(request, template, {
                  email: email,
                  event: event,
                  subscriber: subscriber,
                  error: error,
                  }, content_type='text/html')
