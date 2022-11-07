from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseForbidden, HttpResponse

import requests


class IndexView(View):
    def get(self, request, gallery_id):
        return render(request, 'viewer/view.html',
                      {
                          'gallery_id': gallery_id,
                      })


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
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
    }
    res = requests.get(image_url, headers=header)
    if res.status_code == 403:
        return HttpResponseForbidden()
    return HttpResponse(res.content, content_type=res.headers['Content-Type'])
