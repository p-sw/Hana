from django.contrib import admin

from .models import Tag, Favorites

# Register your models here.
admin.site.register(Tag)
admin.site.register(Favorites)
