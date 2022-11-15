from django.core.management.base import BaseCommand, CommandError
from main.models import Tag

import requests
import re
import time
import threading

from bs4 import BeautifulSoup as bs

from requests.exceptions import ConnectionError
from requests.exceptions import ConnectTimeout
from urllib3.exceptions import ProtocolError

MALE_PREFIX = 9792

tag_queue = list(range(96, 123))
artists_queue = list(range(96, 123))
series_queue = list(range(96, 123))
characters_queue = list(range(96, 123))

locker = threading.Lock()


class Command(BaseCommand):
    help = "Get tags from hitomi.la, and update database."

    def add_arguments(self, parser):
        parser.add_argument('--tabs', type=str, help="Tags, Artists, Series, Characters, Languages, All", default="all")
        parser.add_argument('--threads', type=int, help="Number of threads", default=2)
        parser.add_argument('--singlethread', type=bool, help="Single thread", default=False)

    def handle(self, *args, **options):
        t = options['tabs']
        all_workers = []
        if not options['singlethread']:
            for i in range(options['threads']):
                if t.lower() == "all" or t.lower() == "tags":
                    all_workers.append(threading.Thread(target=self.get_tags))
                if t.lower() == "all" or t.lower() == "artists":
                    all_workers.append(threading.Thread(target=self.get_artists))
                if t.lower() == 'all' or t.lower() == "series":
                    all_workers.append(threading.Thread(target=self.get_series))
                if t.lower() == "all" or t.lower() == "characters":
                    all_workers.append(threading.Thread(target=self.get_characters))

            for worker in all_workers:
                worker.start()

            for worker in all_workers:
                worker.join()
        else:
            if t.lower() == "all" or t.lower() == "tags":
                self.get_tags()
            if t.lower() == "all" or t.lower() == "artists":
                self.get_artists()
            if t.lower() == 'all' or t.lower() == "series":
                self.get_series()
            if t.lower() == "all" or t.lower() == "characters":
                self.get_characters()

        if t.lower() == "all" or t.lower() == "languages":
            self.stdout.write(self.style.WARNING("Adding language tags..."))
            languages = [
                "indonessian", "javanese", "catalan", "cebuano", "czech", "danish", "german", "estonian",
                "english", "spanish", "esperanto", "french", "hindi", "icelandic", "italian", "latin", "hungarian",
                "dutch", "norwegian", "polish", "portuguese", "romanian", "albanian", "russian", "slovak",
                "serbian", "finnish", "swedish", "tagalog", "vietnamese", "turkish", "greek", "bulgarian",
                "mongolian", "russian", "ukrainian", "hebrew", "arabic", "persian", "korean", "thai", "chinese",
                "japanese"
            ]
            for language in languages:
                success = False
                while not success:
                    try:
                        res = requests.get(f"https://ltn.hitomi.la/n/index-{language}.nozomi", headers={
                            "Content-Type": "arraybuffer",
                            "origin": "https://hitomi.la",
                            "referer": "https://hitomi.la/"
                        })
                        if res.status_code == 200:
                            success = True
                            counts = len(res.content) // 4
                            Tag.objects.update_or_insert(name=language, tagtype="language", gallery_count=counts)
                        else:
                            time.sleep(1)
                    except (ConnectionError, ConnectTimeout, ProtocolError):
                        self.stdout.write(self.style.WARNING(f"Failed to connect to hitomi.la"))
                        self.stdout.write(self.style.WARNING(f"Retrying..."))
                        continue




    def get_tags(self):
        global tag_queue
        tag_expression = r'\/tag.+.html">\n\s+(.+)\n\s+</a>\n\s+(\(\d+\))'
        r = None

        self.stdout.write(f"Thread {threading.get_ident()}: Taking tags...")

        i = "idle"

        while tag_queue:
            locker.acquire()
            i = tag_queue.pop(0)
            locker.release()
            self.stdout.write(self.style.SUCCESS(f"Thread {threading.get_ident()}: Taking {chr(i)} part of tags..."))
            req_success = False
            while not req_success:
                try:
                    if i == 96:
                        r = requests.get('https://hitomi.la/alltags-123.html')
                    else:
                        r = requests.get(f"https://hitomi.la/alltags-{chr(i)}.html", timeout=5)
                    if r.status_code == 200:
                        req_success = True
                    elif r.status_code == 404:
                        return
                    else:
                        r = None
                        continue
                except (ConnectionError, ConnectTimeout, ProtocolError):
                    self.stdout.write(self.style.WARNING(f"Failed to connect to hitomi.la"))
                    self.stdout.write(self.style.WARNING(f"Retrying..."))
                    r = None
            if not r:
                self.stdout.write(self.style.ERROR(f"Finally failed to connect to hitomi.la"))
                return
            content = bs(r.content, "html.parser").prettify()
            m = re.findall(tag_expression, content)
            tags = [i[0] for i in m]
            for index, tag in enumerate(tags):
                if len(tag.split(' ')[-1]) != 1:  # no gender tag
                    tag_name = tag
                    tag_type = "tag"
                elif ord(tag.split(' ')[-1]) == MALE_PREFIX:
                    tag_name = tag[:-1]
                    tag_type = "male"
                else:
                    tag_name = tag[:-1]
                    tag_type = "female"
                tag_count = int(re.compile(r"\((\d+)\)").match(m[index][1]).group(1))
                Tag.objects.update_or_insert(name=tag_name, tagtype=tag_type, gallery_count=tag_count)

        self.stdout.write(f"Thread {threading.get_ident()}: Done artists thread with job {i}")

    def get_artists(self):
        global artists_queue
        artist_expression = r'\/artist.+.html">\n\s+(.+)\n\s+</a>\n\s+(\(\d+\))'
        r = None
        self.stdout.write(f"Thread {threading.get_ident()}: Taking artists...")

        i = "idle"

        while artists_queue:
            locker.acquire()
            i = artists_queue.pop(0)
            locker.release()
            self.stdout.write(self.style.SUCCESS(f"Thread {threading.get_ident()}: Taking {chr(i)} part of artists..."))
            req_success = False
            while not req_success:
                try:
                    if i == 96:
                        r = requests.get('https://hitomi.la/allartists-123.html')
                    else:
                        r = requests.get(f"https://hitomi.la/allartists-{chr(i)}.html", timeout=5)

                    if r.status_code == 200:
                        req_success = True
                    elif r.status_code == 404:
                        return
                    else:
                        r = None
                        continue
                except (ConnectionError, ConnectTimeout, ProtocolError):
                    self.stdout.write(self.style.WARNING(f"Failed to connect to hitomi.la"))
                    self.stdout.write(self.style.WARNING(f"Retrying..."))
                    r = None
            if not r:
                self.stdout.write(self.style.ERROR(f"Finally failed to connect to hitomi.la"))
                return
            content = bs(r.content, "html.parser").prettify()
            artists = re.findall(artist_expression, content)
            for artist in artists:
                Tag.objects.update_or_insert(name=artist[0],
                                             tagtype="artist",
                                             gallery_count=int(re.match(r"\((\d+)\)", artist[1]).group(1)))

        self.stdout.write(f"Thread {threading.get_ident()}: Done artists thread with job {i}")

    def get_series(self):
        global series_queue
        series_expression = r'\/series.+.html">\n\s+(.+)\n\s+</a>\n\s+(\(\d+\))'
        r = None

        self.stdout.write(f"Thread {threading.get_ident()}: Taking series...")

        i = "idle"

        while series_queue:
            locker.acquire()
            i = series_queue.pop(0)
            locker.release()
            self.stdout.write(self.style.SUCCESS(f"Thread {threading.get_ident()}: Taking {chr(i)} part of series..."))
            req_success = False
            while not req_success:
                try:
                    if i == 96:
                        r = requests.get('https://hitomi.la/allseries-123.html')
                    else:
                        r = requests.get(f"https://hitomi.la/allseries-{chr(i)}.html", timeout=5)
                    if r.status_code == 200:
                        req_success = True
                    elif r.status_code == 404:
                        return
                    else:
                        r = None
                        continue
                except (ConnectionError, ConnectTimeout, ProtocolError):
                    self.stdout.write(self.style.WARNING(f"Failed to connect to hitomi.la"))
                    self.stdout.write(self.style.WARNING(f"Retrying..."))
                    r = None
            if not r:
                self.stdout.write(self.style.ERROR(f"Finally failed to connect to hitomi.la"))
                return
            content = bs(r.content, "html.parser").prettify()
            serieses = re.findall(series_expression, content)
            for series in serieses:
                Tag.objects.update_or_insert(name=series[0],
                                             tagtype="series",
                                             gallery_count=int(re.match(r"\((\d+)\)", series[1]).group(1)))

        self.stdout.write(f"Thread {threading.get_ident()}: Done series thread with job {i}")

    def get_characters(self):
        global characters_queue
        character_expression = r'\/character.+.html">\n\s+(.+)\n\s+</a>\n\s+(\(\d+\))'
        r = None

        self.stdout.write(f"Thread {threading.get_ident()}: Taking characters...")

        i = 'idle'

        while characters_queue:
            locker.acquire()
            i = characters_queue.pop(0)
            locker.release()
            self.stdout.write(self.style.SUCCESS(f"Thread {threading.get_ident()}: Taking {chr(i)} part of characters..."))
            req_success = False
            while not req_success:
                try:
                    if i == 96:
                        r = requests.get('https://hitomi.la/allcharacters-123.html')
                    else:
                        r = requests.get(f"https://hitomi.la/allcharacters-{chr(i)}.html", timeout=5)

                    if r.status_code == 200:
                        req_success = True
                    elif r.status_code == 404:
                        return
                    else:
                        r = None
                        continue
                except (ConnectionError, ConnectTimeout, ProtocolError):
                    self.stdout.write(self.style.WARNING(f"Failed to connect to hitomi.la"))
                    self.stdout.write(self.style.WARNING(f"Retrying..."))
                    r = None
            if not r:
                self.stdout.write(self.style.ERROR(f"Finally failed to connect to hitomi.la"))
                return
            content = bs(r.content, "html.parser").prettify()
            characters = re.findall(character_expression, content)
            for character in characters:
                Tag.objects.update_or_insert(name=character[0],
                                             tagtype="character",
                                             gallery_count=int(re.match(r"\((\d+)\)", character[1]).group(1)))
        self.stdout.write(f"Thread {threading.get_ident()}: Done characters thread with job {i}")
