from django.contrib import admin
from camp.models import SponsorshipLevel, Sponsor


class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'sponsorship', 'order', )
    list_editable = ('order', )
    list_filter = ('sponsorship', )
    search_fields = ('name', )


class SponsorshipLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'event', 'price',
                    'order', )
    list_editable = ('order', )
    list_filter = ('event__name', )
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ('name', 'event', )


admin.site.register(Sponsor, SponsorAdmin)
admin.site.register(SponsorshipLevel, SponsorshipLevelAdmin)
