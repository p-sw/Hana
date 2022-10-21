from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.generic import View
from django.urls import reverse

from secrets import token_urlsafe
import smtplib
from email.mime.text import MIMEText
from constance import config

from . import models


class UserRegister(View):
    def get(self, request):
        return render(request, 'user/register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if User.objects.filter(username=username).exists():
            return render(request, 'user/register.html', {
                'form': {
                    "username": {
                        "error": "이미 사용중인 사용자 이름입니다."
                    }
                }
            })
        if User.objects.filter(email=email).exists():
            return render(request, 'user/register.html', {
                'form': {
                    "email": {
                        "error": "이미 가입된 이메일입니다."
                    }
                }
            })
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()
        return render(request, 'user/register.html')


class UserLogin(View):
    def get(self, request):
        return render(request, 'user/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:  # success
            login(request, user)
            return render(request, 'user/login.html')
        else:  # fail
            return render(request, 'user/login.html', {'error': '잘못된 사용자 정보입니다.'})


class ChangePasswordAuth(View):
    def get(self, request):
        return render(request, 'user/change_password_auth.html')

    def post(self, request):
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            token = token_urlsafe(20)
            models.PasswordChangeToken(token=token, email=email).save()
            msg = MIMEText(f'비밀번호 변경 링크: {config.ROOT_URL}{reverse("user:change_password_token", args=[token])}')
            print(f"Connecting to SMTP server {config.MAIL_SERVER}:{config.MAIL_PORT}")
            smtp = smtplib.SMTP_SSL(config.MAIL_SERVER, config.MAIL_PORT)
            print(f"Logging in using account {config.MAIL_USERNAME}, password {config.MAIL_PASSWORD}")
            smtp.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)

            msg['Subject'] = '[HANA] 비밀번호 변경 링크'
            msg['From'] = config.MAIL_USERNAME
            msg['To'] = email

            print(f"Sending email from {config.MAIL_USERNAME} to {email}...")
            smtp.send_message(msg)
            print("Email sent.")
            smtp.quit()
            print("Quit SMTP server.")
            return render(request, 'user/change_password_middle_auth.html', {'email': email})
        else:
            return render(request, 'user/change_password_auth.html', {'error': '존재하지 않는 이메일입니다.'})


class ChangePassword(View):
    def get(self, request, token):
        if models.PasswordChangeToken.objects.filter(token=token).exists():
            return render(request, 'user/change_password.html', {'token': token})
        else:
            return render(request, 'general/404.html')

    def post(self, request, token):
        if models.PasswordChangeToken.objects.filter(token=token).exists():
            token_obj = models.PasswordChangeToken.objects.get(token=token)
            user = User.objects.get(email=token_obj.email)
            user.set_password(request.POST.get('password'))
            user.save()
            token_obj.delete()
            return render(request, 'user/change_password_success.html')
        else:
            return render(request, 'general/404.html')
