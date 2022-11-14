from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt

import requests
import json

from main.models import Tag


# Create your views here.
@login_required
def image_proxy(request):
    image_url = request.GET.get('url')
    referer = request.GET.get('gallery', '')
    header = {
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": f"https://hitomi.la/reader/{referer}.html" if referer else "https://hitomi.la/",
        "sec-ch-ua": '"Chromium";v="106", "Not;A=Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "image",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-site",
        "user-agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/106.0.0.0 Safari/537.36"
    }
    res = requests.get(image_url, headers=header)
    if res.status_code == 403:
        return HttpResponseForbidden()
    return HttpResponse(res.content, content_type=res.headers['Content-Type'])


def nozomi_proxy(request):
    res = requests.get("https://ltn.hitomi.la/index-all.nozomi", headers={
        "Content-Type": "arraybuffer",
        "Range": f"bytes={request.GET.get('start')}-{request.GET.get('end')}"
    })

    if res.status_code in [200, 206]:
        headers = {
            "Content-Type": "arraybuffer",
            "Content-Range": res.headers['Content-Range'],
            "Content-Length": res.headers['Content-Length'],
        }
        return HttpResponse(res.content, headers=headers, status=res.status_code)
    else:
        return HttpResponse(status=res.status_code)


def js_proxy(request):
    res = requests.get(request.GET.get('url'), headers={
        "Content-Type": "text/javascript",
    })

    if res.status_code == 200:
        return HttpResponse(res.content, content_type="text/javascript")
    else:
        return HttpResponse(status=res.status_code)


def galleryblock_proxy(request):
    res = requests.get(f"https://ltn.hitomi.la/galleryblock/{request.GET.get('id')}.html", headers={
        "Content-Type": "text/html",
    })

    if res.status_code == 200:
        return HttpResponse(res.content, content_type="text/html")
    else:
        return HttpResponse(status=res.status_code)


@csrf_exempt
def get_recommendation_tag(request):
    POST: dict = json.loads(request.body)
    current_name = POST.get("tag")
    ban_ids = POST.get("ban")

    def get_tags(name_query: str, excludes: list = None):
        if excludes:
            return Tag.objects.exclude(id__in=excludes).filter(name__startswith=name_query).values_list('id', 'tagtype', 'name')[:5]
        else:
            return Tag.objects.filter(name__startswith=name_query).values_list('id', 'tagtype', 'name')[:5]

    tag_suggests_1 = get_tags(current_name, ban_ids)
    res = tag_suggests_1
    if len(tag_suggests_1) != 5:
        tag_suggests_2 = get_tags(current_name, ban_ids)
        res = tag_suggests_2
        if len(tag_suggests_2) != 5:
            total_tag_suggests = (list(tag_suggests_1) + list(tag_suggests_2))[:5]
            res = total_tag_suggests

    return JsonResponse({tag_id: f"{tag_type}:{tag_name}" for tag_id, tag_type, tag_name in res})
