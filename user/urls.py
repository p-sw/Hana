app_name = "user"

from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.UserLogin.as_view(), name='login'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('register_success/', views.RegisterSuccessTestView.as_view(), name='register_success'),
    path('change_password/', views.ChangePasswordAuth.as_view(), name='change_password'),
    path('change_password/<str:token>/', views.ChangePassword.as_view(), name='change_password_token'),
]
