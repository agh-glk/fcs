from django.http.response import HttpResponse


def register_task_server(request, task_id):
    print task_id
    return HttpResponse('OK')