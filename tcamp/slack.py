import json
import requests
from django.conf import settings


def post_registration(ticket):
    text = '%s %s just registered for Transparency Camp!' % (ticket.first_name, ticket.last_name)
    payload = {
        'channel': '#transparencycamp',
        'icon_emoji': 'tent',
        'username': settings.SLACK_USERNAME,
        'text': text,
    }
    params = {'token': settings.SLACK_TOKEN}
    requests.post(settings.SLACK_URL, params=params, data=json.dumps(payload))
