from django.db import models


class TagManager(models.Manager):
    def update_or_insert(self, **kwargs):
        tag = self.filter(**kwargs).first()
        if not tag:
            tag = self.create(**kwargs)
        return tag


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    tagtype = models.CharField(max_length=10, choices=(
        ('female', 'Female Tag'),
        ('male', 'Male Tag'),
        ('tag', 'No Gender Tag'),
        ('artist', 'Artist'),
        ('series', 'Series'),
        ('character', 'Character'),
        ('language', 'Language'),
    ))
    gallery_count = models.IntegerField(default=-1)

    objects = TagManager()

    def __str__(self):
        return f"{self.tagtype}:{self.name}"


class Favorites(models.Model):
    id = models.BigAutoField(primary_key=True)
    gallery_id = models.BigIntegerField()
    user_id = models.IntegerField()

    def __str__(self):
        return f"{self.user_id}::{self.gallery_id}"
