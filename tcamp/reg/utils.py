from django.http import HttpResponse, HttpResponseRedirect

def cors_allow_all(orig_func):
    def new_func(request, *args, **kwargs):
        if request.method == 'OPTIONS':
            response = HttpResponse()
        else:
            response = orig_func(request, *args, **kwargs)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = '*'
        response['Access-Control-Allow-Headers'] = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', '*')
        response['Access-Control-Max-Age'] = '172800'
        return response
    return new_func

def memodict(f):
    """ Memoization decorator for a function taking a single argument """
    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret 
    return memodict().__getitem__