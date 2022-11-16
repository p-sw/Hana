from django.contrib import admin

from .models import Tag, Favorites

# Register your models here.


class TagAdmin(admin.ModelAdmin):
    search_fields = ['tagtype', 'name']


admin.site.register(Tag, TagAdmin)
admin.site.register(Favorites)
