import requests
import urllib3.exceptions
import datetime

from .models import Tag


def get_galleries_for_tag():  # weekly job
    print(f"{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))} - Gallery Counter Started")
    for tag in Tag.objects.all():
        print(f"Getting gallery count for {tag.tagtype}:{tag.name}")
        url = f"https://ltn.hitomi.la/n"
        area = tag.tagtype
        language = "all"
        tag = tag.name

        if tag.tagtype == "female" or tag.tagtype == "male":
            area = "tag"
            tag = f"{tag.tagtype}:{tag.name}"
        elif tag.tagtype == "language":
            area = ""
            language = tag.name
            tag = "index"

        url = f"{url}/{area}/{tag}-{language}.nozomi"
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
                    print("Retrying request due to status code: "+str(res.status_code))
                    continue
                req_success = True
            except (requests.exceptions.ConnectTimeout,
                    requests.exceptions.ConnectionError,
                    urllib3.exceptions.MaxRetryError):
                print("Retrying request due to ConnectionErrors")
                continue

        tag.gallery_count = len(res.content) / 4
        print(f"Get gallery count for {tag.tagtype}:{tag.name} - {len(res.content) / 4}")
        tag.save()
    # korean timezone
    print(f"{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))} - Gallery Counter Finished")
