from django.contrib import admin
from reg.models import *
from sked.admin import EventAdmin

class TicketTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(TicketType, TicketTypeAdmin)

admin.site.register(Sale)
admin.site.register(Ticket)
admin.site.register(CouponCode)

# class TicketTypeInline(admin.TabularInline):
#     model = TicketType
#     sortable_field_name = 'position'
# EventAdmin.inlines.append(TicketTypeInline)