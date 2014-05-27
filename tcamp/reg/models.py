from sked.models import Event
from django.db import models
from django.db.models.query import QuerySet
from django_extras.db.models.fields import MoneyField, PercentField
from django_extensions.db.fields import PostgreSQLUUIDField
import datetime
import shortuuid
import uuid
from reg.utils import *


class TicketType(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    expires = models.DateTimeField(null=True)
    max_tickets = models.PositiveIntegerField(help_text="How many tickets of this type to sell; 0 indicates unlimited tickets.")
    price = models.DecimalField(max_digits=20, decimal_places=2)
    enabled = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    online = models.BooleanField(default=True)
    onsite = models.BooleanField(default=False)

    _count = None
    @property
    def count(self):
        if self._count is None:
            self._count = Ticket.objects.filter(event=self.event, success=True, type=self).count()
        return self._count

    @property
    def short_name(self):
        return shorten_ticket_type(self.name)

    def is_expired(self):
        return datetime.datetime.now() > self.expires

    def is_sold_out(self):
        return self.max_tickets > 0 and self.max_tickets <= self.count

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['position']


@memodict
def shorten_ticket_type(name):
    return name.split(":")[0].replace(" ", "_").lower()


class CouponCode(models.Model):
    event = models.ForeignKey(Event)
    code = models.CharField(max_length=255)
    discount = PercentField(default=100)
    max_tickets = models.IntegerField(help_text="How many tickets to allow to obtain this discount; 0 indicates unlimited tickets.")
    is_staff = models.BooleanField(help_text="Indicates that people that use this code are staff; has no real effect but is useful for tabulating.", default=False)

    def __str__(self):
        return self.code


class Sale(models.Model):
    event = models.ForeignKey(Event)

    first_name = models.TextField(blank=True)
    last_name = models.TextField(blank=True)
    email = models.EmailField(blank=True)

    address1 = models.TextField(blank=True)
    address2 = models.TextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zip = models.CharField(max_length=255, blank=True)

    coupon_code = models.ForeignKey(CouponCode, null=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True)

    transaction_id = models.CharField(max_length=255, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    def send_receipts(self):
        from reg.email_utils import *
        if self.email:
            send_html_email_template(subject='TransparencyCamp Receipt', to_addresses=[self.email], sender="info@transparencycamp.org", template='reg/email_sale.html', context={'sale': self}, images=[])

        for ticket in self.ticket_set.all():
            if ticket.email and ticket.email != self.email:
                send_html_email_template(subject='TransparencyCamp Receipt', to_addresses=[ticket.email], sender="info@transparencycamp.org", template='reg/email_ticket.html', context={'ticket': ticket}, images=[])

    def __unicode__(self):
        return u" ".join((self.first_name, self.last_name))

    def __str__(self):
        return u" ".join((self.first_name, self.last_name))


# some barcode convenience methods for tickets
class TicketQuerySet(QuerySet):
    def filter(self, *args, **kwargs):
        if 'short_barcode' in kwargs:
            kwargs['barcode'] = shortuuid.decode(kwargs['short_barcode'])
            del kwargs['short_barcode']
        return super(TicketQuerySet, self).filter(*args, **kwargs)


class TicketManager(models.Manager):
    def get_query_set(self):
        return TicketQuerySet(self.model)


AMBASSADOR_PROGRAM_CHOICES = (
    ('no', 'No thank you'),
    ('new', "Yes, I'm a new attendee and would like to be paired with an ambassador."),
    ('vet', "Yes, I would like to be an ambassador, and welcome new members of our community."),
    ('maybe', "Maybe; please keep me informed."),
)


class Ticket(models.Model):
    event = models.ForeignKey(Event)
    sale = models.ForeignKey(Sale, null=True)
    type = models.ForeignKey(TicketType)

    barcode = PostgreSQLUUIDField(db_index=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(db_index=True)

    title = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    twitter = models.CharField(max_length=127, verbose_name="Twitter Handle", blank=True)
    website = models.CharField(max_length=255, blank=True)

    diet_vegetarian = models.BooleanField(default=False, verbose_name="Vegetarian")
    diet_vegan = models.BooleanField(default=False, verbose_name="Vegan")
    diet_gluten_free = models.BooleanField(default=False, verbose_name="Gluten-free")
    diet_allergies = models.BooleanField(default=False, verbose_name="Allergies")
    diet_allergies_desc = models.TextField(blank=True, verbose_name="Description (allergies)")
    diet_other = models.BooleanField(default=False, verbose_name="Other dietary needs")
    diet_other_desc = models.TextField(blank=True, verbose_name="Description (other dietary needs)")

    attend_day1 = models.BooleanField(default=True, verbose_name="Friday")
    attend_day2 = models.BooleanField(default=True, verbose_name="Saturday")

    lobby_day = models.BooleanField(default=False, verbose_name="Do you plan to attend the Sunlight Network's Lobby Day?")
    ambassador_program = models.CharField(default="no", choices=AMBASSADOR_PROGRAM_CHOICES, max_length=12, verbose_name="Would you like to be part of the TCamp Ambassador Program?")

    subscribe = models.BooleanField(default=False, verbose_name="Please subscribe me to emails from the Sunlight Foundation")

    success = models.BooleanField(default=False, db_index=True)

    checked_in = models.DateTimeField(null=True, default=None)

    objects = TicketManager()

    @property
    def clean_twitter(self):
        if self.twitter and self.twitter.startswith("@"):
            return self.twitter[1:]
        else:
            return self.twitter

    @property
    def short_barcode(self):
        qrcode_uuid = uuid.UUID(self.barcode)
        return shortuuid.encode(qrcode_uuid)

    def __unicode__(self):
        return u" ".join((self.first_name, self.last_name))

    def __str__(self):
        return u" ".join((self.first_name, self.last_name))
