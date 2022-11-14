from django.db import models


class TagManager(models.Manager):
    def update_or_insert(self, name, tagtype):
        tag = self.filter(name=name, tagtype=tagtype).first()
        if not tag:
            tag = self.create(name=name, tagtype=tagtype)
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

    objects = TagManager()

    def __str__(self):
        return f"{self.tagtype}:{self.name}"
