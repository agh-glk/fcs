from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import redirect
import forms
from models import Quota, UserData
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            username, first_name, last_name, passwd, email, qta = \
                [form.cleaned_data[x] for x in ['username', 'first_name', 'last_name', 'password', 'email', 'quota']]
            user = User.objects.create_user(username=username, first_name=first_name,
                                            last_name=last_name, password=passwd, email=email)
            user.save()
            user_data = UserData.objects.create(user=user)
            user_data.save()
            quota = Quota.objects.create(user=user, mock_field=qta)
            quota.save()

            return HttpResponseRedirect('/reg_scs/')
    else:
        form = forms.RegistrationForm()
    return render(request, 'register.html', {'form': form})


def registration_successful(request):
    return render(request, 'reg_scs.html')


def login_user(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            passwd = form.cleaned_data['password']
            user = authenticate(username=username, password=passwd)
            if user is not None:
                login(request, user)
                return render(request, 'log_scs.html')
    else:
        if request.user.is_authenticated():
            return HttpResponse('You are already logged in')
    form = forms.LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('/')


@login_required()
def change_password(request):
        if request.method == 'POST':
            form = forms.ChangePasswordForm(request.POST)
            if form.is_valid():
                old_passwd, passwd1, passwd2 = \
                    [form.cleaned_data[x] for x in ['old_password', 'password', 'password_again']]
                if request.user.check_password(old_passwd) and passwd1 == passwd2:
                    request.user.set_password(passwd1)
                    request.user.save()
                    logout(request)
                    return render(request, 'passwd_changed_scs.html')
        form = forms.ChangePasswordForm()
        return render(request, 'change_password.html', {'form': form})