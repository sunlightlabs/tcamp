from sked.models import Event


def current_event(request):
    return {
        'CURRENT_EVENT': Event.objects.public_current(request)
    }
