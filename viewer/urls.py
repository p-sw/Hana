app_name = "viewer"

from django.urls import path

from . import views

urlpatterns = [
    path('<int:gallery_id>', views.IndexView.as_view(), name='index'),
    path('image', views.image_proxy, name='image_proxy'),
]