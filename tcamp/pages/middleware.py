from django.http import Http404
from django.conf import settings

from pages.views import page


class PagesMiddleware(object):
    """ An almost exact copy of FlatpageFallbackMiddleware from Django.
    """

    def process_response(self, request, response):

        if response.status_code != 404:
            return response

        try:
            return page(request, request.path_info)
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response
