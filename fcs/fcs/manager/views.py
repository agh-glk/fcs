from django.shortcuts import render, render_to_response
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework_swagger import SWAGGER_SETTINGS

import forms
from models import Task, CrawlingType
from oauth2_provider.models import Application
from tables import TaskTable
from django_tables2 import RequestConfig
from django.http import StreamingHttpResponse
from datetime import datetime


def index(request):
    return render(request, 'index.html')


@login_required()
def list_tasks(request):
    tasks = Task.objects.filter(user=request.user)
    table = TaskTable(tasks)
    RequestConfig(request).configure(table)
    return render(request, 'tasks/list.html', {'table': table})


@login_required()
def add_task(request):
    if request.method == 'POST':
        form = forms.CreateTaskForm(data=request.POST, user=request.user)
        if form.is_valid():
            name, priority, whitelist, blacklist, max_links, expire, types = \
                [form.cleaned_data[x] for x in ['name', 'priority', 'whitelist', 'blacklist',
                                                'max_links', 'expire', 'type']]
            _crawling_types = CrawlingType.objects.filter(type__in=map(lambda x: int(x), types))
            Task.objects.create_task(request.user, name, priority, expire, _crawling_types, whitelist, blacklist, max_links)
            messages.success(request, 'New task created.')
            return redirect('list_tasks')
    else:
        form = forms.CreateTaskForm(user=request.user)
    return render(request, 'tasks/add.html', {'form': form})


@login_required()
def show_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user.id)
    form = forms.EditTaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        messages.success(request, "Task %s updated." % task.name)
        return redirect('list_tasks')
    return render(request, 'tasks/show.html', {'task': task, 'form': form, 'ratings': range(1, 6)})


@login_required()
def api_keys(request):
    application = Application.objects.filter(user=request.user).first()
    return render(request, 'api_keys.html', {'application': application})


@login_required()
def pause_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user.id)
    if task.finished:
        messages.error(request, 'Task already finished!')
    elif not task.active:
        messages.error(request, 'Task already paused!')
    else:
        task.pause()
        messages.success(request, 'Task %s paused.' % task.name)
    return redirect('list_tasks')


@login_required()
def resume_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user.id)
    if task.finished:
        messages.error(request, 'Task already finished!')
    elif task.active:
        messages.error(request, 'Task already in progress!')
    else:
        task.resume()
        messages.success(request, 'Task %s resumed.' % task.name)
    return redirect('list_tasks')


@login_required()
def stop_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user.id)
    if task.finished:
        messages.error(request, 'Task already finished!')
    else:
        task.stop()
        messages.success(request, 'Task %s stopped.' % task.name)
    return redirect('list_tasks')


@login_required()
def get_data(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user.id)
    task.last_data_download = datetime.now()
    task.save()
    return StreamingHttpResponse("Data From Crawler")


@login_required()
def show_quota(request):
    quota = request.user.quota
    return render(request, 'show_quota.html', {'quota': quota})


def api_docs_resources(request):
    host = request.build_absolute_uri()
    return render_to_response('api_docs/resources.json', {"host": host.rstrip('/')}, mimetype='application/json')


def api_docs_declaration(request, path):
    protocol = "https" if request.is_secure() else "http"
    api_path = SWAGGER_SETTINGS['api_path']
    api_full_uri = "%s://%s%s" % (protocol, request.get_host(), api_path)
    return render_to_response('api_docs/' + path + '.json', {"host": api_full_uri.rstrip('/')}, mimetype='application/json')
