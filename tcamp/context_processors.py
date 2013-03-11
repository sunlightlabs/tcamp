from django.conf import settings


def basic_settings(request):
    return {
        'FAVICON': settings.FAVICON,
        'APPLE_TOUCH_ICON': settings.APPLE_TOUCH_ICON,
        'SHARING_IMAGE': settings.SHARING_IMAGE,
        'FB_APP_ID': settings.FB_APP_ID,
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
    }
