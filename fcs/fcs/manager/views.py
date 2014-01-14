from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

import forms
from models import Task, CrawlingType, User
from oauth2_provider.models import Application
from tables import TaskTable
from django_tables2 import RequestConfig
from django.http import StreamingHttpResponse
from datetime import datetime


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
                return redirect('index')
            elif user:
                messages.error(request, "Account is not activated. Check your email.")
            else:
                messages.error(request, "Authentication failed. Incorrect username or password.")
    else:
        if request.user.is_authenticated():
            return HttpResponse('You are already logged in')
        else:
            form = forms.LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_user(request):
    logout(request)
    messages.success(request, "Logout successful.")
    return redirect('index')


@login_required()
def change_password(request):
        if request.method == 'POST':
            form = forms.ChangePasswordForm(request.POST)
            if form.is_valid():
                old_passwd, passwd1, passwd2 = \
                    [form.cleaned_data[x] for x in ['old_password', 'password', 'password_again']]
                if request.user.check_password(old_passwd):
                    request.user.set_password(passwd1)
                    request.user.save()
                    logout(request)
                    messages.success(request, "Password changed successfully. Please log-in again.")
                    return redirect('index')
                else:
                    messages.error(request, "Old password is incorrect.")
        else:
            form = forms.ChangePasswordForm()
        return render(request, 'change_password.html', {'form': form})


@login_required()
def list_tasks(request):
    tasks = Task.objects.filter(user=request.user)
    table = TaskTable(tasks)
    RequestConfig(request).configure(table)
    return render(request, 'tasks/list.html', {'table': table})


@login_required()
def add_task(request):
    if request.method == 'POST':
        form = forms.CreateTaskForm(request.POST)
        if form.is_valid():
            name, priority, whitelist, blacklist, max_links, expire, types = \
                [form.cleaned_data[x] for x in ['name', 'priority', 'whitelist', 'blacklist',
                                                'max_links', 'expire', 'type']]
            _crawling_types = CrawlingType.objects.filter(type__in=map(lambda x: int(x), types))
            Task.objects.create_task(request.user, name, priority, expire, _crawling_types, whitelist, blacklist, max_links)
            messages.success(request, 'New task created.')
            return redirect('list_tasks')
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
        return redirect('list_tasks')
    return render(request, 'tasks/show.html', {'task': task, 'form': form, 'ratings': range(1, 6)})


@login_required()
def api_keys(request):
    application = Application.objects.filter(user=request.user).first()
    if request.method == 'POST':
        Application.objects.create(user=request.user, client_type=Application.CLIENT_CONFIDENTIAL,
                                   authorization_grant_type=Application.GRANT_PASSWORD)
        return redirect('api_keys')
    return render(request, 'api_keys.html', {'application': application})


@login_required()
def pause_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.user != request.user:
        raise Http404
    if task.finished:
        messages.error(request, u'Task already finished!')
    elif not task.active:
        messages.error(request, u'Task already paused!')
    else:
        task.pause()
        messages.success(request, u'Task %s paused.' % task.name)
    return redirect('list_tasks')


@login_required()
def resume_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.user != request.user:
        raise Http404
    if task.finished:
        messages.error(request, u'Task already finished!')
    elif task.active:
        messages.error(request, u'Task already in progress!')
    else:
        task.resume()
        messages.success(request, u'Task %s resumed.' % task.name)
    return redirect('list_tasks')


@login_required()
def stop_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.user != request.user:
        raise Http404
    if task.finished:
        messages.error(request, u'Task already finished!')
    else:
        task.stop()
        messages.success(request, u'Task %s stopped.' % task.name)
    return redirect('list_tasks')


@login_required()
def get_data(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.last_data_download = datetime.now()
    task.save()
    return StreamingHttpResponse("Data From Crawler")


@login_required()
def edit_user_data(request):
    user = get_object_or_404(User, id=request.user.id)
    form = forms.EditUserForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        messages.success(request, "Your data updated!")
        return redirect('index')
    return render(request, 'edit_user_data.html', {'form': form})


@login_required()
def show_quota(request):
    quota = request.user.quota
    return render(request, 'show_quota.html', {'quota': quota})


