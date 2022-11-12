app_name = "viewer"

from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('<int:gallery_id>', login_required(views.IndexView.as_view()), name='index'),
]