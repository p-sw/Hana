from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls', namespace='user')),
    path('/', include('main.urls', namespace='main')),
    path('view/', include('viewer.urls', namespace='viewer')),
]
