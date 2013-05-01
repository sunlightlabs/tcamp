import urlparse

from django.core.urlresolvers import resolve
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST


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
