from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
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
            user = User.objects.create(username=username, password=passwd, email=email)
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


@csrf_exempt
def login(request):
    if request.method == 'GET':
        if request.session.get('user_id', False):
            return HttpResponse('You are already logged in')
    if request.method == 'POST':
        try:
            username = request.POST['username']
            passwd = request.POST['password']
            user = User.objects.get(username=username)
            if user.check_password(passwd):
                request.session['user_id'] = user.id
                return HttpResponse('You have successfully logged in')
        except:
            pass
        return HttpResponse('You have not logged in')
    return render(request, 'login.html')


def logout_views(request):
    logout(request)
    return redirect('/')