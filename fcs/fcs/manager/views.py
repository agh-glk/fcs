from django.shortcuts import render, render_to_response
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework_swagger import SWAGGER_SETTINGS
from fcs.manager.forms import TaskFilterForm

import forms
from models import Task
from oauth2_provider.models import Application
from tables import TaskTable
from django_tables2 import RequestConfig
from django.http import StreamingHttpResponse, HttpResponseRedirect
from datetime import datetime


def index(request):
    """
    Main page.
    """
    return render(request, 'index.html')


@login_required()
def list_tasks(request):
    """
    List of all current user's tasks.
    """
    choice = int(request.GET.get('tasks', TaskFilterForm.ALL))
    page_size = int(request.GET.get('page_size', 25))
    tasks = Task.objects.filter(user=request.user)
    f = TaskFilterForm(initial={'tasks': choice, 'page_size': page_size})
    if choice == TaskFilterForm.FINISHED:
        tasks = tasks.filter(finished=True)
    elif choice == TaskFilterForm.RUNNING:
        tasks = tasks.filter(finished=False).filter(active=True)
    elif choice == TaskFilterForm.PAUSED:
        tasks = tasks.filter(finished=False).filter(active=False)
    table = TaskTable(tasks)
    RequestConfig(request, paginate={'per_page': page_size}).configure(table)
    return render(request, 'tasks/list.html', {'table': table, 'filter_form': f})


@login_required()
def add_task(request):
    """
    View for creating new task.
    """
    if request.method == 'POST':
        form = forms.CreateTaskForm(data=request.POST, user=request.user)
        if form.is_valid():
            name, priority, whitelist, blacklist, max_links, expire, mime_type, start_links = \
                [form.cleaned_data[x] for x in ['name', 'priority', 'whitelist', 'blacklist',
                                                'max_links', 'expire', 'mime_type', 'start_links']]

            Task.objects.create_task(request.user, name, priority, expire, start_links, whitelist, blacklist, max_links, mime_type)
            messages.success(request, 'New task created.')
            return redirect('list_tasks')
    else:
        form = forms.CreateTaskForm(user=request.user)
    return render(request, 'tasks/add.html', {'form': form})


@login_required()
def show_task(request, task_id):
    """
    Allows pausing, stopping and resuming task. Shows its details. Additionally, parameters of running or paused task
     can be changed.
    """
    task = get_object_or_404(Task, id=task_id, user=request.user.id)
    form = forms.EditTaskForm(request.POST or None, instance=task)
    # TODO: display proper feedback ratings
    fieldset_value = task.finished and 'disabled' or ''
    if form.is_valid():
        form.save()
        messages.success(request, "Task %s updated." % task.name)
        return redirect('list_tasks')
    return render(request, 'tasks/show.html', {'task': task, 'form': form, 'ratings': range(1, 6),
                  'fieldset_value': fieldset_value})


@login_required()
def api_keys(request):
    """
    Shows Application Key and Secret Key for REST API.
    """
    application = Application.objects.filter(user=request.user).first()
    return render(request, 'api_keys.html', {'application': application})


@login_required()
def pause_task(request, task_id):
    """
    Pauses task and redirect to tasks list.
    """
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
    """
    Resumes task and redirect to tasks list.
    """
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
    """
    Stops task and redirect to tasks list.
    """
    task = get_object_or_404(Task, id=task_id, user=request.user.id)
    if task.finished:
        messages.error(request, 'Task already finished!')
    else:
        task.stop()
        messages.success(request, 'Task %s stopped.' % task.name)
    return redirect('list_tasks')


@login_required()
def get_data(request, task_id, size):
    """
    Downloads data gathered by crawler.
    """
    task = get_object_or_404(Task, id=task_id, user=request.user.id)
    task.last_data_download = datetime.now()
    task.save()
    if task.server:
        return HttpResponseRedirect(task.server.address + '/get_data?size=' + str(size))
    else:
        return StreamingHttpResponse("No task server to download data from")


@login_required()
def show_quota(request):
    """
    Shows limitations for tasks, described by Quota object.
    """
    quota = request.user.quota
    return render(request, 'show_quota.html', {'quota': quota})


def api_docs_resources(request):
    """
    Swagger view generating REST API documentation.
    """
    host = request.build_absolute_uri()
    return render_to_response('api_docs/resources.json', {"host": host.rstrip('/')}, mimetype='application/json')


def api_docs_declaration(request, path):
    """
    Swagger view generating REST API documentation.
    """
    protocol = "https" if request.is_secure() else "http"
    api_path = SWAGGER_SETTINGS['api_path']
    api_full_uri = "%s://%s%s" % (protocol, request.get_host(), api_path)
    return render_to_response('api_docs/' + path + '.json', {"host": api_full_uri.rstrip('/')}, mimetype='application/json')
