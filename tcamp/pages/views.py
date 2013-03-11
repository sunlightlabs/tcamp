from django.shortcuts import render, get_object_or_404
# from django.template import Template
# from django.utils.safestring import mark_safe
from pages.models import Page


def page(request, path):

    path = "/%s/" % path.strip('/')
    p = get_object_or_404(Page, path=path, is_published=True)
    return render(request, p.as_renderable(), {"page": p})
