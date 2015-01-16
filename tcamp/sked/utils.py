_current_event = None
def get_current_event():
    global _current_event
    
    if not _current_event:
        from sked.models import Event
        _current_event = Event.objects.current()

    return _current_event