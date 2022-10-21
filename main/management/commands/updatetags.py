from django.core.management.base import BaseCommand, CommandError
from main.models import Tag

import requests
import re
import time

from bs4 import BeautifulSoup as bs

from requests.exceptions import ConnectionError
from requests.exceptions import ConnectTimeout
from urllib3.exceptions import ProtocolError


class Command(BaseCommand):
    help = "Get tags from hitomi.la, and update database."

    def add_arguments(self, parser):
        parser.add_argument('tabs', nargs='+', type=str, help="Tags, Artists, Series, Characters, All")

    def handle(self, *args, **options):
        t = options['tabs'][0]
        if t.lower() == "all":
            self.get_tags()
            self.get_artists()
            self.get_series()
            self.get_characters()
        elif t.lower() == "tags":
            self.get_tags()
        elif t.lower() == "artists":
            self.get_artists()
        elif t.lower() == "series":
            self.get_series()
        elif t.lower() == "characters":
            self.get_characters()

        self.stdout.write(self.style.SUCCESS('Successfully updated tags'))
        self.stdout.write(self.style.WARNING("Adding language tags..."))
        languages = [
            "indonessian",
            "javanese",
            "catalan",
            "cebuano",
            "czech",
            "danish",
            "german",
            "estonian",
            "english",
            "spanish",
            "esperanto",
            "french",
            "hindi",
            "icelandic",
            "italian",
            "latin",
            "hungarian",
            "dutch",
            "norwegian",
            "polish",
            "portuguese",
            "romanian",
            "albanian",
            "russian",
            "slovak",
            "serbian",
            "finnish",
            "swedish",
            "tagalog",
            "vietnamese",
            "turkish",
            "greek",
            "bulgarian",
            "mongolian",
            "russian",
            "ukrainian",
            "hebrew",
            "arabic",
            "persian",
            "korean",
            "thai",
            "chinese",
            "japanese"
        ]
        for language in languages:
            Tag.objects.update_or_insert(language, "language")

    def get_tags(self):
        MALE_PREFIX = 9792
        FEMALE_PREFIX = 9794

        tag_expression = r'\/tag.+.html">\n\s+(.+)\n'
        r = None

        for i in range(96, 123):
            for _ in range(3):
                try:
                    if i == 96:
                        r = requests.get('https://hitomi.la/alltags-123.html')
                    else:
                        r = requests.get(f"https://hitomi.la/alltags-{chr(i)}.html", timeout=5)
                except (ConnectionError, ConnectTimeout, ProtocolError):
                    self.stdout.write(self.style.WARNING(f"Failed to connect to hitomi.la"))
                    self.stdout.write(self.style.WARNING(f"Retrying..."))
                    r = None
                    time.sleep(2)
            if not r:
                self.stdout.write(self.style.ERROR(f"Finally failed to connect to hitomi.la"))
                return
            content = bs(r.content).prettify()
            tags = re.findall(tag_expression, content)
            for tag in tags:
                self.stdout.write(self.style.SUCCESS(f"Tag: {tag}"))
                if len(tag.split(' ')[-1]) != 1:  # no gender tag
                    tag_name = tag
                    tag_type = "tag"
                elif ord(tag.split(' ')[-1]) == MALE_PREFIX:
                    tag_name = tag[:-1]
                    tag_type = "male"
                else:
                    tag_name = tag[:-1]
                    tag_type = "female"
                self.stdout.write(self.style.SUCCESS(f"Tag Name: {tag_name}"))
                self.stdout.write(self.style.SUCCESS(f"Tag Type: {tag_type}"))
                Tag.objects.update_or_insert(tag_name, tag_type)

    def get_artists(self):
        artist_expression = r'\/artist.+.html">\n\s+(.+)\n'
        r = None

        for i in range(96, 123):
            for _ in range(3):
                try:
                    if i == 96:
                        r = requests.get('https://hitomi.la/allartists-123.html')
                    else:
                        r = requests.get(f"https://hitomi.la/allartists-{chr(i)}.html", timeout=5)
                except (ConnectionError, ConnectTimeout, ProtocolError):
                    self.stdout.write(self.style.WARNING(f"Failed to connect to hitomi.la"))
                    self.stdout.write(self.style.WARNING(f"Retrying..."))
                    r = None
                    time.sleep(2)
            if not r:
                self.stdout.write(self.style.ERROR(f"Finally failed to connect to hitomi.la"))
                return
            content = bs(r.content).prettify()
            artists = re.findall(artist_expression, content)
            for artist in artists:
                self.stdout.write(self.style.SUCCESS(f"Artist: {artist}"))
                Tag.objects.update_or_insert(artist, "artist")

    def get_series(self):
        series_expression = r'\/series.+.html">\n\s+(.+)\n'
        r = None

        for i in range(96, 123):
            for _ in range(3):
                try:
                    if i == 96:
                        r = requests.get('https://hitomi.la/allseries-123.html')
                    else:
                        r = requests.get(f"https://hitomi.la/allseries-{chr(i)}.html", timeout=5)
                except (ConnectionError, ConnectTimeout, ProtocolError):
                    self.stdout.write(self.style.WARNING(f"Failed to connect to hitomi.la"))
                    self.stdout.write(self.style.WARNING(f"Retrying..."))
                    r = None
                    time.sleep(2)
            if not r:
                self.stdout.write(self.style.ERROR(f"Finally failed to connect to hitomi.la"))
                return
            content = bs(r.content).prettify()
            serieses = re.findall(series_expression, content)
            for series in serieses:
                self.stdout.write(self.style.SUCCESS(f"Series: {series}"))
                Tag.objects.update_or_insert(series, "series")

    def get_characters(self):
        character_expression = r'\/character.+.html">\n\s+(.+)\n'
        r = None

        for i in range(96, 123):
            for _ in range(3):
                try:
                    if i == 96:
                        r = requests.get('https://hitomi.la/allcharacters-123.html')
                    else:
                        r = requests.get(f"https://hitomi.la/allcharacters-{chr(i)}.html", timeout=5)
                except (ConnectionError, ConnectTimeout, ProtocolError):
                    self.stdout.write(self.style.WARNING(f"Failed to connect to hitomi.la"))
                    self.stdout.write(self.style.WARNING(f"Retrying..."))
                    r = None
                    time.sleep(2)
            if not r:
                self.stdout.write(self.style.ERROR(f"Finally failed to connect to hitomi.la"))
                return
            content = bs(r.content).prettify()
            characters = re.findall(character_expression, content)
            for character in characters:
                self.stdout.write(self.style.SUCCESS(f"Characters: {character}"))
                Tag.objects.update_or_insert(character, "character")
