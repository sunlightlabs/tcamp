from tcamp.sked.models import Event
from django.db import models
from django_extras.db import models as de_models

class TicketType(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    expires = models.DateTimeField()
    max_tickets = models.PositiveIntegerField(help_text="How many tickets of this type to sell; 0 indicates unlimited tickets.")
    price = de_models.MoneyField(decimal_places=2)
    enabled = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)

class CouponCode(models.Model):
    event = models.ForeignKey(Event)
    code = models.CharField(max_length=255)
    discount = de_models.PercentField(default=100)
    max_tickets = models.PositiveIntegerField(help_text="How many tickets to allow to obtain this discount; 0 indicates unlimited tickets.")

class Sale(models.Model):
    event = models.ForeignKey(Event)

    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField()

    address1 = models.TextField()
    address2 = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)

    coupon_code = models.ForeignKey(CouponCode)
    amount = models.MoneyField(decimal_places=2, blank=True)

    success = models.BooleanField(default=False)

AMBASSADOR_PROGRAM_CHOICES = (
    ('no', 'No thank you'),
    ('new', "Yes, I'm a new attendee and would like to be paired with an ambassador."),
    ('vet', "Yes, I would like to be an ambassador, and welcome new members of our community.")
    ('maybe', "Maybe; please keep me informed.")
)
class Ticket(models.Model):
    event = models.ForeignKey(Event)
    sale = models.ForeignKey(Sale, null=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_lenght=255)
    email = models.EmailField()

    title = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    twitter = models.CharField(max_length=127, label="Twitter Handle", blank=True)
    website = models.CharField(max_length=255, blank=True)

    diet_vegetarian = models.BooleanField(default=False)
    diet_vegan = models.BooleanField(default=False)
    diet_gluten_free = models.BooleanField(default=False)
    diet_allergies = models.BooleanField(default=False)
    diet_allergies_desc = models.TextField(blank=True)
    diet_other = models.BooleanField(default=False)
    diet_other_desc = models.TextField(blank=True)

    lobby_day = models.BooleanField(default=False)
    ambassador_program = models.CharField(default="no")

    subscribe = models.BooleanField(default=False)

    success = models.BooleanField(default=False)