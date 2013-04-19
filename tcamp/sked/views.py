import re
import datetime

from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from django.views.generic import (ListView, DetailView, CreateView,
                                  UpdateView, RedirectView)
from django.views.generic.edit import DeletionMixin
from camp.forms import BootstrapErrorList
from sked.models import Event, Session
from sked.forms import SessionForm


class SessionList(ListView):
    model = Session
    context_object_name = 'session_list'

    def get_queryset(self):
        return self.model.objects.published().filter(
            event__slug=self.kwargs.get('event_slug'))

    def get_context_data(self, **kwargs):
        context = super(SessionList, self).get_context_data(**kwargs)
        days = [d.replace(tzinfo=timezone.get_current_timezone()) for
                d in self.get_queryset().dates('start_time', 'day', order="ASC")]
        event = get_object_or_404(Event, slug=self.kwargs.get('event_slug'))
        context['event'] = event
        context['days'] = days
        context['now'] = timezone.now()
        return context


class SessionDetail(DetailView):
    model = Session
    context_object_name = 'session'
    preview = None

    def get_object(self):
        obj = get_object_or_404(self.model,
                                slug=self.kwargs.get('slug'),
                                event__slug=self.kwargs.get('event_slug'))
        # Need to either be in preview mode, or dealing with a public event.
        if not (self.preview or obj.is_public):
            raise Http404

        return obj

    def get_context_data(self, **kwargs):
        context = super(SessionDetail, self).get_context_data(**kwargs)
        context['event'] = context['session'].event
        context['is_permalink'] = True
        if self.preview:
            messages.warning(self.request,
                             '''This is a
                                preview url. We'll be adding sessions
                                to the wall over the next few hours. If this
                                is your session,
                                you'll get an email with the time and location
                                if it's added. Check your
                                email now, though, for a link that will
                                let you make edits if something doesn't look right.''')
        return context


class SessionCrudMixin(object):
    model = Session
    context_object_name = 'session'
    form_class = SessionForm

    def _get_event(self):
        return get_object_or_404(Event, slug=self.kwargs.get('event_slug'))

    def _mux_inputlist(self, data, keys, **kwargs):
        ''' Builds a list of dicts from several QueryDict.getlist() calls.
            In this case, speakers[name], speakers[email], speakers[twitter]
            get zipped into:
            [{
                'name': 'foo',
                'email': 'foo@example.com',
                'twitter': '@foo'
            }]
            '''
        keypat = re.compile(r'[\w_-]+\[([^\]]+)\]')  # matches foo[bar], captures bar in grp 1
        objects = zip(*[data.getlist(key) for key in keys])
        resolved_keys = [keypat.search(key).group(1) for key in keys]
        return [dict(zip(resolved_keys, obj)) for obj in objects]

    def get_form_kwargs(self):
        kwargs = super(SessionCrudMixin, self).get_form_kwargs()
        kwargs.update(error_class=BootstrapErrorList)
        return kwargs

    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()

        # use POST data or instance dict to prefill form depending on method.
        if kwargs.get('data'):
            data = kwargs['data'].copy()
            data.update(
                speakers=self._mux_inputlist(kwargs['data'],
                                             ['speakers[name]',
                                              'speakers[twitter]',
                                              'speakers[position]', ]),
                extra_data=self._mux_inputlist(kwargs['data'],
                                               ['extra_data[has_slides]', ])[0],
                event=self._get_event().id
            )
            data['speakers'][0]['email'] = kwargs['data'].getlist('speakers[email]')[0]
        else:
            try:
                data = self.object.__dict__
            except AttributeError:
                data = None
        if data:
            kwargs['data'] = data
        form = form_class(**kwargs)
        return form

    def get_context_data(self, **kwargs):
        context = super(SessionCrudMixin, self).get_context_data(**kwargs)
        context['event'] = self._get_event()
        context['form'] = kwargs.get('form', SessionForm())
        return context

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return '{0}preview/'.format(self.object.get_absolute_url())

    def form_valid(self, form):
        if self.object:
            messages.success(self.request, 'Your changes have been saved.')
        return super(SessionCrudMixin, self).form_valid(form)


class CreateSession(SessionCrudMixin, CreateView):
    pass


class UpdateSession(SessionCrudMixin, UpdateView, DeletionMixin):
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_public:
            return HttpResponseRedirect(self.object.get_absolute_url())
        if not (self.object.edit_key in self.request.GET):
            raise PermissionDenied()
        return super(UpdateSession, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        delete = self.get_form_kwargs().get('data', {}).get('delete')
        if delete == 'delete':
            self.success_url = self._get_event().get_absolute_url()
            messages.success(self.request, 'Your session was deleted.')
            return self.delete(request, *args, **kwargs)
        return super(UpdateSession, self).post(request, *args, **kwargs)


class RedirectFromPk(RedirectView):
    def get_redirect_url(self, **kwargs):
        obj = get_object_or_404(Session, pk=kwargs['pk'])
        return obj.get_absolute_url()
