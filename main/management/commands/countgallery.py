from django.core.management.base import BaseCommand, CommandError
from main.models import Tag

import urllib3.exceptions
import datetime
import requests
import threading

id_index = 1
locker = threading.Lock()


class Command(BaseCommand):
    help = "Count gallery in each tag"

    def add_arguments(self, parser):
        parser.add_argument('--worker', type=int, help="Worker number", default=1)

    def handle(self, *args, **options):
        db_max = Tag.objects.count()
        print(f"{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))} - Gallery Counter Start")
        workers = []
        worker_max = options["worker"]
        new_worker = None
        while id_index <= db_max:
            if len(workers) < worker_max:
                new_worker = threading.Thread(target=self.gallery_count)
                workers.append(new_worker)
                new_worker.start()
            for worker in workers:
                if not worker.is_alive():
                    workers.remove(worker)
        new_worker.join()
        print(f"{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))} - Gallery Counter End")

    @staticmethod
    def gallery_count():
        global id_index
        locker.acquire()
        tag = Tag.objects.filter(id__exact=id_index).first()
        id_index += 1
        locker.release()
        print(f"Working on {tag.tagtype}:{tag.name}")
        url = f"https://ltn.hitomi.la/n/"
        area = tag.tagtype
        language = "all"
        tag_r = tag.name

        if tag.tagtype == "female" or tag.tagtype == "male":
            area = "tag/"
            tag_r = f"{tag.tagtype}:{tag.name}"
        elif tag.tagtype == "language":
            area = ""
            language = tag.name
            tag_r = "index"

        url = f"{url}{area}{tag_r.rstrip(' ')}-{language}.nozomi"
        print(f"Final request URL: {url}")
        headers = {
            "Content-Type": "arraybuffer",
            "origin": "https://hitomi.la",
            "Referer": "https://hitomi.la",
        }

        req_success = False
        res = None
        while not req_success:
            try:
                res = requests.get(url, headers)
                if res.status_code not in [200, 206]:
                    print(f"{url} - Retrying request due to status code: " + str(res.status_code))
                    if res.status_code == 404:
                        return
                    continue
                req_success = True
            except (requests.exceptions.ConnectTimeout,
                    requests.exceptions.ConnectionError,
                    urllib3.exceptions.MaxRetryError):
                print(f"{url} - Retrying request due to ConnectionErrors")
                continue

        tag.gallery_count = int(len(res.content) / 4)
        print(f"Get gallery count for {tag.tagtype}:{tag.name} - {int(len(res.content) / 4)} galleries")
        tag.save()
