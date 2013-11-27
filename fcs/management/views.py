from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def index(request):
    return render(request, 'index.html')

def register(request):
    return render(request, 'register.html')

@csrf_exempt
def login(request):
    if request.method == 'GET':
        if request.session.get('user_id', False):
            return HttpResponse('You are already logged in')
    if request.method == 'POST':
        try:
            u = request.POST['username']
            p = request.POST['password']
            user = User.objects.get(username=u)
            if user.check_password(p):
                request.session['user_id'] = user.id
                return HttpResponse('You have successfully logged in')
        except:
            pass
        return HttpResponse('You have not logged in')
    return render(request, 'login.html')