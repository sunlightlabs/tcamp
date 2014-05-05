import json
import requests
from django.conf import settings

USERNAME = 'tcampbot'
URL = 'https://sunlight.slack.com/services/hooks/incoming-webhook'


def post_registration(data):
    text = '%s %s just registered for Transparency Camp!' % (data['first_name'], data['last_name'])
    payload = {
        'channel': '#transparencycamp',
        'icon_emoji': 'tent',
        'username': USERNAME,
        'text': text
    }
    params = {'token': settings.SLACK_TOKEN}
    requests.post(URL, params=params, data=json.dumps(payload))
