from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.PasswordChangeToken)
admin.site.register(models.InviteToken)