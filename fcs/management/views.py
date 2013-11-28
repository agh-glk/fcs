from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import redirect
import forms
from models import Quota, ClientData


def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            username, passwd, email, qta = \
                [form.cleaned_data[x] for x in ['username', 'password', 'email', 'quota']]
            user = User.objects.create_user(username=username, password=passwd, email=email)
            user.save()
            quota = Quota.objects.create(mock_field=int(qta))
            quota.save()
            client = ClientData.objects.create(user=user, quota=quota)
            client.save()

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