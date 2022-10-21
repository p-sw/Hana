from django.shortcuts import render

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.views.generic import View


class UserRegister(View):
    def get(self, request):
        return render(request, 'user/register.html')

    def post(self, request):
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()
        return render(request, 'user/register.html')


class UserLogin(View):
    def get(self, request):
        return render(request, 'user/login.html')

    def post(self, request):
        username = request.form.get('username')
        password = request.form.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:  # success
            login(request, user)
            return render(request, 'user/login.html')
        else:  # fail
            return render(request, 'user/login.html')
