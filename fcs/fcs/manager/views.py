from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import redirect
import forms
from django.contrib.auth.decorators import login_required
from models import Task, CrawlingType
from django.shortcuts import get_object_or_404


def index(request):
    return render(request, 'index.html')


def login_user(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            passwd = form.cleaned_data['password']
            user = authenticate(username=username, password=passwd)
            if user is not None and user.is_active:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('/')
    else:
        if request.user.is_authenticated():
            return HttpResponse('You are already logged in')
        else:
            form = forms.LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_user(request):
    logout(request)
    messages.success(request, "Logout successful.")
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
        else:
            form = forms.ChangePasswordForm()
        return render(request, 'change_password.html', {'form': form})


@login_required()
def list_tasks(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/list.html', {'tasks': tasks})


@login_required()
def add_task(request):
    if request.method == 'POST':
        form = forms.CreateTaskForm(request.POST)
        if form.is_valid():
            name, priority, whitelist, blacklist, max_links, expire, types = \
                [form.cleaned_data[x] for x in ['name', 'priority', 'whitelist', 'blacklist',
                                                'max_links', 'expire', 'type']]
            _crawling_types = CrawlingType.objects.filter(type__in=map(lambda x: int(x), types))
            Task.create_task(request.user, name, priority, expire, _crawling_types, whitelist, blacklist, max_links)
            messages.success(request, 'New task created.')
            return redirect('/tasks/list/')
    else:
        form = forms.CreateTaskForm()
    return render(request, 'tasks/add.html', {'form': form})


@login_required()
def show_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user.id)
    form = forms.EditTaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        messages.success(request, "Task %s updated" % task.name)
        return redirect('/tasks/list/')
    return render(request, 'tasks/show.html', {'task': task, 'form':form})