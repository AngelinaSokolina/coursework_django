from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .forms import UserRegisterForm, UserLoginForm
from .services import send_verification_email, email_verification_token
from .models import User


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_verification_email(user, request)
            messages.success(request, 'Регистрация прошла успешно! Подтвердите email.')
            return redirect('users:login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('mailing:home')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('mailing:home')


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and email_verification_token.check_token(user, token):
        user.is_verified = True
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Email подтверждён!')
        return redirect('mailing:home')
    else:
        messages.error(request, 'Ссылка недействительна или истекла.')
        return redirect('users:login')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        print(f"=== ССЫЛКА ДЛЯ СБРОСА ПАРОЛЯ ДЛЯ {email} ===")
        print(f"Перейдите по ссылке: http://127.0.0.1:8000/users/password-reset/")
        return super().form_valid(form)