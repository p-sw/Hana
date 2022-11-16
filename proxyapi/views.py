import urllib3.exceptions
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

import requests
import json

from main.models import Tag, Favorites


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
    except (urllib3.exceptions.MaxRetryError, requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
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
        except (requests.exceptions.ConnectionError, urllib3.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
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
    try:
        res = requests.get(request.GET.get('url'), headers={
            "Content-Type": "text/javascript",
        })
    except (requests.exceptions.ConnectionError, urllib3.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        return HttpResponse(status=500)

    if res.status_code == 200:
        return HttpResponse(res.content, content_type="text/javascript")
    else:
        return HttpResponse(status=res.status_code)


def galleryblock_proxy(request):
    try:
        res = requests.get(f"https://ltn.hitomi.la/galleryblock/{request.GET.get('id')}.html", headers={
            "Content-Type": "text/html",
        })
    except (requests.exceptions.ConnectionError, urllib3.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        return HttpResponse(status=500)

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
            return Tag.objects.exclude(
                id__in=excludes
            ).filter(**filter_kwargs).order_by('-gallery_count').values_list('id', 'tagtype', 'name')
        else:
            return Tag.objects.filter(**filter_kwargs).order_by('-gallery_count').values_list(
                'id',
                'tagtype',
                'name',
            )

    def suggest_trys(trys):
        totals = []
        for try_dict in trys:
            try_dict["excludes"] += [i[0] for i in totals]
            res = get_tags(**try_dict)
            if len(res) == search_result_limit and len(totals) == 0:
                return res
            elif len(totals+list(res)) >= search_result_limit:
                return totals+list(res)
            else:
                totals += res
                continue
        return totals

    result = suggest_trys([
        {
            "type_query": query_type if query_type else "female",
            "type_filter": "startswith",
            "name_query": current_name,
            "name_filter": "startswith",
            "excludes": ban_ids
        },
        {
            "type_query": query_type if query_type else "male",
            "type_filter": "startswith",
            "name_query": current_name,
            "name_filter": "startswith",
            "excludes": ban_ids
        },
        {
            "type_query": query_type,
            "type_filter": "startswith",
            "name_query": current_name,
            "name_filter": "startswith",
            "excludes": ban_ids
        },
        {
            "type_query": query_type if query_type else "female",
            "type_filter": "startswith",
            "name_query": current_name,
            "name_filter": "in",
            "excludes": ban_ids
        },
        {
            "type_query": query_type if query_type else "male",
            "type_filter": "startswith",
            "name_query": current_name,
            "name_filter": "in",
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

    return JsonResponse(
        {tag_id: f"{tag_type}:{tag_name}" for tag_id, tag_type, tag_name in result}
    )


def get_favorite_by_gallery(request):
    gallery_id = request.GET.get('id')
    user_id = request.user.id

    if not user_id:
        return HttpResponse(status=403)

    return JsonResponse({"exists": Favorites.objects.filter(user_id=user_id, gallery_id=gallery_id).exists()})


@csrf_exempt
def toggle_favorite(request):
    POST: dict = json.loads(request.body)
    gallery_id = POST.get("galleryid")
    user_id = request.user.id

    if not user_id:
        return HttpResponse(status=403)

    obj = Favorites.objects.filter(user_id=user_id, gallery_id=gallery_id)

    if obj.exists():
        obj.delete()
        return JsonResponse({"exists": False})
    else:
        Favorites.objects.create(user_id=user_id, gallery_id=gallery_id)
        return JsonResponse({"exists": True})


def get_favorite_list(request):
    user_id = request.user.id

    if not user_id:
        return HttpResponse(status=403)

    result = Favorites.objects.filter(user_id=user_id).values_list('gallery_id', flat=True)
    return JsonResponse({"galleries": list(result)})
