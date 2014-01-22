import re

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.csrf import CsrfViewMiddleware


class PathRestrictedProxy(object):
    """ a mixin for creating middleware that allows you to restrict
        behavior to only those url fragments declared in settings """
    path_rexp = r''
    proxy_class = object
    proxy = None

    def __init__(self, *args, **kwargs):
        patterns = getattr(settings, 'SESSIONABLE_URL_PATTERNS', (r'.'))
        self.path_rexp = r'(%s)' % r'|'.join(patterns)
        self.proxy = self.proxy_class(*args, **kwargs)

    def is_restricted(self, request):
        if re.search(self.path_rexp, request.path):
            return False
        return True

    def process_request(self, request):
        print 'checking whether request is sessionable'
        if not self.is_restricted(request):
            try:
                self.proxy.process_request(request)
            except AttributeError:
                pass

    def process_response(self, request, response):
        if self.is_restricted(request):
            return response
        try:
            return self.proxy.process_response(request, response)
        except AttributeError:
            return response


class ConditionalSessionMiddleware(PathRestrictedProxy):
    proxy_class = SessionMiddleware


class ConditionalAuthenticationMiddleware(PathRestrictedProxy):
    proxy_class = AuthenticationMiddleware

    def process_request(self, request):
        if self.is_restricted(request):
            # Always set a user, even if it's AnonymousUser
            request.user = AnonymousUser()
        else:
            self.proxy.process_request(request)


class ConditionalMessageMiddleware(PathRestrictedProxy):
    proxy_class = MessageMiddleware


class ConditionalCsrfViewMiddleware(PathRestrictedProxy):
    proxy_class = CsrfViewMiddleware

    # always process on request
    def process_view(self, request, callback, callback_args, callback_kwargs):
        self.proxy.process_view(request, callback, callback_args, callback_kwargs)
