app_name = "main"

from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('search', login_required(views.SearchView.as_view()), name='search'),
]