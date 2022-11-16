from django.urls import path

from . import views

app_name = "proxy"

FAVORITE_API = [
    path('favorite/get-favorite-by-id', views.get_favorite_by_gallery, name='get_favorite_by_id'),
    path('favorite/toggle-favorite', views.toggle_favorite, name='toggle_favorite'),
]

urlpatterns = [
    path('get-image', views.image_proxy, name='image_proxy'),
    path('get-nozomi', views.nozomi_proxy, name='nozomi_proxy'),
    path('get-js', views.js_proxy, name='js_proxy'),
    path('get-galleryblock', views.galleryblock_proxy, name='galleryblock_proxy'),
    path('get-recommendation-tag', views.get_recommendation_tag, name='get_recommendation_tag'),
] + FAVORITE_API
