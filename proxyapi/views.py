import urllib3.exceptions
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt

import requests
import json
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectTimeout

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
    try:
        res = requests.get(image_url, headers=header, timeout=3)
    except (MaxRetryError, ConnectTimeout):
        return HttpResponse(status=408)
    print("While proxying image: ", res.status_code)
    if res.status_code == 200:
        return HttpResponse(res.content, content_type=res.headers['Content-Type'])
    else:
        header = res.headers
        del header["Connection"]
        return HttpResponse(res.content, headers=header, status=res.status_code)


def nozomi_proxy(request):
    area = request.GET.get('area', '')
    compressed = request.GET.get('comp_prefix', '')
    tag = request.GET.get('tag', 'index')
    language = request.GET.get('language', 'all')
    start_byte = request.GET.get('start', '')
    end_byte = request.GET.get('end', '')

    request_url = "https://ltn.hitomi.la/"
    if compressed:
        request_url += f"{compressed}/"
    if area:
        request_url += f"{area}/"
    request_url += f"{tag}-{language}.nozomi"

    req_header = {
        "Content-Type": "arraybuffer",
        "origin": "https://hitomi.la/",
        "Referer": "https://hitomi.la/"
    }
    if start_byte and end_byte:
        req_header['Range'] = f"bytes={start_byte}-{end_byte}"

    res = None
    fail = True
    while fail:
        try:
            res = requests.get(request_url, headers=req_header)
            fail = False
        except (requests.exceptions.ConnectionError, urllib3.exceptions.ConnectionError):
            continue
    if not res:
        return HttpResponse(status=500)

    if res.status_code in [200, 206]:
        # repack
        if compressed:
            return HttpResponse(res.content, content_type="arraybuffer", status=res.status_code)
        else:
            return HttpResponse(res.content, content_type="arraybuffer", status=res.status_code)
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
    current_name = POST.get("tag") or ""
    query_type = POST.get("type") or ""
    ban_ids = POST.get("ban") or []

    search_result_limit = 8

    def get_tags(type_query: str, type_filter: str, name_query: str, name_filter: str, excludes: list = None):
        filter_kwargs = {}
        if type_query:
            filter_kwargs["tagtype__"+type_filter] = type_query
        if name_query:
            filter_kwargs["name__"+name_filter] = name_query
        if excludes:
            return Tag.objects.exclude(id__in=excludes).filter(**filter_kwargs).values_list('id', 'tagtype', 'name')
        else:
            return Tag.objects.filter(**filter_kwargs).values_list('id', 'tagtype', 'name')

    def suggest_trys(trys):
        totals = []
        for try_dict in trys:
            res = get_tags(**try_dict)
            if len(res) == 5:
                return res
            else:
                totals += res
                continue
        return totals

    result = suggest_trys([
        {
            "type_query": query_type,
            "type_filter": "startswith",
            "name_query": current_name,
            "name_filter": "startswith",
            "excludes": ban_ids
        },
        {
            "type_query": query_type,
            "type_filter": "startswith",
            "name_query": current_name,
            "name_filter": "in",
            "excludes": ban_ids
        }
    ])[:search_result_limit]

    return JsonResponse({tag_id: f"{tag_type}:{tag_name}" for tag_id, tag_type, tag_name in result})
