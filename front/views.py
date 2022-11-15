from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.urls import reverse


class IndexView(TemplateView):
    template_name = 'front/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('main:index'))
        return super().get(request, *args, **kwargs)
