from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseForbidden

import requests

import re
# Create your views here.


class IndexView(View):
    def get(self, request, gallery_id):
        res = requests.get("https://hitomi.la/reader/{gallery_id}.html")
        r = re.compile(r"hitomic\('(?P<provider>[^']+)', '(?P<category_name>[^']+)'\)")
        m = r.match(res.text)
        if not m:
            return HttpResponseForbidden()
        provider = m.group('provider')
        category_name = m.group('category_name')
        return render(request, 'viewer/view.html',
                      {
                          'gallery_id': gallery_id,
                          'provider': provider,
                          'category_name': category_name
                      })
