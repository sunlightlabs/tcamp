from django.contrib import admin
from reg.models import *
from sked.admin import EventAdmin

class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'event')
    list_filter = ('event',)
admin.site.register(TicketType, TicketTypeAdmin)

class SaleAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'event', 'success')
    list_filter = ('event', 'success')
admin.site.register(Sale, SaleAdmin)

class TicketAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'event', 'type', 'success')
    list_filter = ('event', 'type', 'success')
    exclude = ('checked_in',)
admin.site.register(Ticket, TicketAdmin)

class CouponCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'event')
    list_filter = ('event',)
admin.site.register(CouponCode, CouponCodeAdmin)

# class TicketTypeInline(admin.TabularInline):
#     model = TicketType
#     sortable_field_name = 'position'
# EventAdmin.inlines.append(TicketTypeInline)