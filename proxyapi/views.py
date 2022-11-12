from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseForbidden

import requests


# Create your views here.
@login_required
def image_proxy(request):
    image_url = request.GET.get('url')
    referer = request.GET.get('gallery')
    header = {
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": f"https://hitomi.la/reader/{referer}.html",
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
