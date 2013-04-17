from sked.models import Event
from camp.models import Sponsor, SponsorshipLevel


def sponsors(request):
    event = Event.objects.current()
    levels = SponsorshipLevel.objects.for_event(event)
    return {
        'sponsors': [Sponsor.objects.select_related().filter(sponsorship=level) for level in levels],
        'secondary_sponsors': Sponsor.objects.select_related().filter(sponsorship__slug__in=['patrons', 'supporters']),
        'levels': levels,
    }
