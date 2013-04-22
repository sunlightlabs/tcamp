from django.conf import settings


def basic_settings(request):
    return {
        'FAVICON': getattr(settings, 'FAVICON'),
        'APPLE_TOUCH_ICON': getattr(settings, 'APPLE_TOUCH_ICON'),
        'SHARING_IMAGE': getattr(settings, 'SHARING_IMAGE'),
        'FB_APP_ID': getattr(settings, 'FB_APP_ID'),
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID'),
        'CACHEBUSTER': getattr(settings, 'CACHEBUSTER'),
    }
