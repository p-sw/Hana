from django.urls import path

from . import views

app_name = "proxy"

urlpatterns = [
    path('get-image', views.image_proxy, name='image_proxy'),
    path('get-nozomi', views.nozomi_proxy, name='nozomi_proxy'),
    path('get-js', views.js_proxy, name='js_proxy'),
]