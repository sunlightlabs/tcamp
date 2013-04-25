from django.contrib import admin
from brainstorm.models import Subsite, Idea


class SubsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name', )}
    date_hierarchy = 'timestamp'


class IdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'subsite', 'is_public', 'score')
    list_filter = ('subsite', 'is_public', )
    date_hierarchy = 'timestamp'


admin.site.register(Subsite, SubsiteAdmin)
admin.site.register(Idea, IdeaAdmin)
