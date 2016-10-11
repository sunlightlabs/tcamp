from django.contrib import admin
from reg.models import *
from sked.admin import EventAdmin
from sked.utils import get_current_event
from django.core.urlresolvers import reverse
from admin_enhancer.admin import EnhancedModelAdminMixin
from admin_exporter.actions import export_as_csv_action
import traceback

# modified from http://stackoverflow.com/a/9712272/261412
class DefaultFilterMixin(object):
    def changelist_view(self, request, *args, **kwargs):
        from django.http import HttpResponseRedirect
        if self.default_filters:
            try:
                test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
                if test and test[-1] and not test[-1].startswith('?'):
                    url = reverse('admin:%s_%s_changelist' % (self.opts.app_label, self.opts.module_name))
                    filters = []
                    for key, _value in self.default_filters:
                        value = _value() if callable(_value) else _value
                        if not request.GET.has_key(key):
                            filters.append("=".join([key, str(value)]))
                    if filters:
                        return HttpResponseRedirect("%s?%s" % (url, "&".join(filters)))
            except:
                traceback.print_exc()
                pass
        return super(DefaultFilterMixin, self).changelist_view(request, *args, **kwargs)


class TicketTypeAdmin(EnhancedModelAdminMixin, DefaultFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'event')
    list_filter = ('event',)
    default_filters = (('event__id__exact', lambda: get_current_event().id),)
admin.site.register(TicketType, TicketTypeAdmin)

class SaleAdmin(EnhancedModelAdminMixin, DefaultFilterMixin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'event', 'success', 'coupon_code')
    list_filter = ('event', 'success', 'payment_type', 'coupon_code')
    default_filters = (('event__id__exact', lambda: get_current_event().id), ('success__exact', 1))

    def coupon_code(self, obj):
        return obj.coupon_code.code if obj.coupon_code else ""

    def queryset(self, request):
        qs = super(SaleAdmin, self).queryset(request)
        return qs.select_related('coupon_code')
admin.site.register(Sale, SaleAdmin)

class TicketAdmin(EnhancedModelAdminMixin, DefaultFilterMixin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'event', 'type', 'success', 'payment_type', 'coupon_code')
    list_filter = ('event', 'type', 'success', 'sale__payment_type', 'sale__coupon_code')
    exclude = ('checked_in',)
    default_filters = (('event__id__exact', lambda: get_current_event().id), ('success__exact', 1))
    actions = [export_as_csv_action]

    def payment_type(self, obj):
        return dict(PAYMENT_TYPE_CHOICES)[obj.sale.payment_type]

    def coupon_code(self, obj):
        return obj.sale.coupon_code

    def queryset(self, request):
        qs = super(TicketAdmin, self).queryset(request)
        return qs.select_related('sale', 'sale__coupon_code')
admin.site.register(Ticket, TicketAdmin)

class CouponCodeAdmin(EnhancedModelAdminMixin, DefaultFilterMixin, admin.ModelAdmin):
    list_display = ('code', 'event', 'discount_percentage', 'ticket_limit')
    list_filter = ('event',)
    default_filters = (('event__id__exact', lambda: get_current_event().id),)

    def discount_percentage(self, obj):
        return "%s%%" % int(obj.discount)

    def ticket_limit(self, obj):
        return "Unlimited" if obj.max_tickets == 0 else obj.max_tickets
admin.site.register(CouponCode, CouponCodeAdmin)

# class TicketTypeInline(admin.TabularInline):
#     model = TicketType
#     sortable_field_name = 'position'
# EventAdmin.inlines.append(TicketTypeInline)

from admin_exporter.actions import export_as_csv_action
