app_name = "user"

from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.UserLogin, name='login'),
    path('register/', views.UserRegister, name='register')
]