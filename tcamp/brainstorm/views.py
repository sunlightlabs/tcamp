import json
import datetime

from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from brainstorm.models import Subsite, Idea, Vote, OPEN
from brainstorm.forms import IdeaForm


class IdeaList(ListView):
    model = Idea
    context_object_name = 'idea_list'
    ordering = 'most_popular'
    ordering_map = {
        'most_popular': '-score',
        'latest': '-timestamp'
    }

    def get_queryset(self):
        return self.model.objects.with_user_vote(self.request.user).filter(
            subsite__slug=self.kwargs.get('slug'),
            is_public=True).order_by(self.ordering_map.get(self.ordering,
                                                           self.ordering))

    def get_context_data(self, **kwargs):
        # Set up pagination interval before calling super()
        subsite = get_object_or_404(Subsite, slug=self.kwargs.get('slug'))
        self.paginate_by = subsite.ideas_per_page

        context = super(IdeaList, self).get_context_data(**kwargs)
        context['subsite'] = subsite
        context['form'] = self.kwargs.get('form', IdeaForm())
        context['ordering'] = self.ordering
        return context


class IdeaDetail(DetailView):
    model = Idea
    context_object_name = 'idea'

    def get_object(self):
        return get_object_or_404(self.model.objects.with_user_vote(self.request.user),
                                 pk=self.kwargs.get('id'),
                                 subsite__slug=self.kwargs.get('slug'),
                                 is_public=True)

    def get_context_data(self, **kwargs):
        context = super(IdeaDetail, self).get_context_data(**kwargs)
        context['subsite'] = context['idea'].subsite
        context['is_permalink'] = True
        return context


class CreateIdea(CreateView):
    model = Idea
    context_object_name = 'idea'
    form_class = IdeaForm

    def _get_subsite(self):
        return get_object_or_404(Subsite, pk=self.kwargs.get('slug'))

    def get(self, *args, **kwargs):
        return HttpResponse('Unauthorized', status=401)

    def get_form(self, form_class):
        subsite = self._get_subsite()
        kwargs = self.get_form_kwargs()
        kwargs['data'] = kwargs['data'].copy()
        kwargs['data']['subsite'] = subsite.slug
        kwargs['request'] = self.request
        if not self.request.user.is_anonymous():
            kwargs['data']['user'] = self.request.user.id
        form = form_class(**kwargs)
        self.request.session['name'] = form['name'].value()
        self.request.session['email'] = form['email'].value()
        return form

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(CreateIdea, self).get_context_data(**kwargs)
        subsite = self._get_subsite()
        context['subsite'] = subsite
        return context


@require_POST
@login_required
def vote(request, slug, id, format='html'):
    idea_id = int(id)
    vote = int(request.POST.get('vote'))
    if vote not in (-1, 0, 1):
        vote = 0
    idea = get_object_or_404(Idea, pk=idea_id, subsite__slug=slug)
    if idea.subsite.voting_status is not OPEN:
        return HttpResponse('Unauthorized', status=401)

    vobj, new = Vote.objects.get_or_create(user=request.user, idea=idea,
                                           defaults={'value': vote})

    if not vote:
        vobj.delete()
    elif not new:
        vobj.value = vote
        vobj.save()

    idea = Idea.objects.with_user_vote(request.user).get(pk=idea_id,
                                                         subsite__slug=slug)

    if format is 'json':
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
        response_d = {
            'success': True,
            'slug': idea.subsite.slug,
            'id': idea.id,
            'vote': vote,
            'score': idea.score,
            'upvotes': idea.upvotes_label.format(idea.upvotes),
            'downvotes': idea.downvotes_label.format(idea.downvotes),
            'timestamp': vobj.timestamp,
        }
        return HttpResponse(json.dumps(response_d, default=dthandler), content_type="application/json")

    if request.is_ajax():
        return render_to_response('brainstorm/partials/idea_vote.html',
                                  {'idea': idea, 'subsite': idea.subsite},
                                  context_instance=RequestContext(request))

    return redirect(idea)
