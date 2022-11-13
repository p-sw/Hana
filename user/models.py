from django.db import models

from secrets import token_hex


class PasswordChangeToken(models.Model):
    token = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class InviteToken(models.Model):
    token = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        self.token = token_hex(20)
        super().save(*args, **kwargs)
