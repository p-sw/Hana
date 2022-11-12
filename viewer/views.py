from django.shortcuts import render
from django.views.generic import View


class IndexView(View):
    def get(self, request, gallery_id):
        return render(request, 'viewer/view.html',
                      {
                          'gallery_id': gallery_id,
                      })
