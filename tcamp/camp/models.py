from django.db import models

from sked.models import Event


class SponsorshipLevelManager(models.Manager):
    def for_event(qs, event):
        return qs.filter(event__id=event.id)


class SponsorshipLevel(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.IntegerField(help_text='Higher numbers come first', default='0')
    event = models.ForeignKey(Event, related_name='sponsorship_levels')

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    objects = SponsorshipLevelManager()

    class Meta:
        ordering = ('-order', '-price')

    def __unicode__(self):
        return u"%s at %s" % (self.name, self.event)


class SponsorManager(models.Manager):
    def for_event(qs, event):
        return qs.select_related().filter(sponsorship__event__id=event.id)


class Sponsor(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='sponsors/logos')
    thumbnail = models.ImageField(upload_to='sponsors/thumbnails')
    url = models.URLField(blank=True, default='')
    sponsorship = models.ForeignKey(SponsorshipLevel, related_name='sponsors', )
    order = models.IntegerField(blank=True, default=0,
                                help_text='Higher numbers come first')

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    objects = SponsorManager()

    class Meta:
        ordering = ('-sponsorship__order', '-sponsorship__price', '-order', )

    def __unicode__(self):
        return self.name
