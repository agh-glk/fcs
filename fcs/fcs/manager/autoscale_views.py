from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from fcs.manager.models import Task, TaskServer


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def register_task_server(request):
    data = request.DATA
    task_id = int(data['task_id'])
    server_address = data['address']
    try:
        task = Task.objects.get(id=task_id)
        if task.server is not None:
            return Response('Task server already assigned', status=status.HTTP_412_PRECONDITION_FAILED)
        if task.finished:
            return Response('Task already stopped', status=status.HTTP_412_PRECONDITION_FAILED)
        server = TaskServer(address=server_address)
        server.save()
        task.server = server
        task.save()
        return Response({'whitelist': task.whitelist.split(','), 'blacklist': task.blacklist,
                            'max_links': task.max_links, 'crawling_type': 0, 'active': task.active,
                            'query': ''})   # TODO: query
    except Task.DoesNotExist:
        return Response('Task not found', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def unregister_task_server(request):
    data = request.DATA
    task_id = int(data['task_id'])
    try:
        task = Task.objects.get(id=task_id)
        if task.server is None:
            return Response('No task server to unregister', status=status.HTTP_412_PRECONDITION_FAILED)
        if not task.finished:
            return Response('Task not stopped yet', status=status.HTTP_412_PRECONDITION_FAILED)
        task.server = None
        task.save()
        return Response('Task server unregistered')
    except Task.DoesNotExist:
        return Response('Task not found', status=status.HTTP_404_NOT_FOUND)