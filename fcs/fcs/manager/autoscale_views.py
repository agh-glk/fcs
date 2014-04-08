from uuid import uuid4
from django.db.utils import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from fcs.manager.models import Task, TaskServer, Crawler


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
        server = TaskServer(address=server_address, uuid=str(uuid4()))
        server.save()
        task.server = server
        task.save()
        return Response({'whitelist': task.whitelist, 'blacklist': task.blacklist, 'priority': task.priority,
                            'max_links': task.max_links, 'crawling_type': 0, 'active': task.active,
                            'finished': task.finished, 'query': '', "expire_date": str(task.expire_date),
                            'uuid': server.uuid})
                            # TODO: remove query, change crawling type values
    except Task.DoesNotExist:
        return Response('Task not found', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def unregister_task_server(request):
    data = request.DATA
    task_id = int(data['task_id'])
    server_uuid = data['uuid']
    try:
        task = Task.objects.get(id=task_id)
        if task.server is None:
            return Response('No task server to unregister', status=status.HTTP_412_PRECONDITION_FAILED)
        if not task.finished:
            return Response('Task not stopped yet', status=status.HTTP_412_PRECONDITION_FAILED)
        if task.server.uuid != server_uuid:
            return Response('Bad UUID provided', status=status.HTTP_412_PRECONDITION_FAILED)
        server = task.server
        task.server = None
        task.save()
        server.delete()
        return Response('Task server unregistered')
    except Task.DoesNotExist:
        return Response('Task not found', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def stop_task(request):
    data = request.DATA
    task_id = int(data['task_id'])
    server_uuid = data['uuid']
    try:
        task = Task.objects.get(id=task_id)
        if task.server is None:
            return Response('No task server assigned - cannot stop task', status=status.HTTP_412_PRECONDITION_FAILED)
        if task.server.uuid != server_uuid:
            return Response('Bad UUID provided', status=status.HTTP_412_PRECONDITION_FAILED)
        task.stop()
        return Response('Task stopped')
    except Task.DoesNotExist:
        return Response('Task not found', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def register_crawler(request):
    data = request.DATA
    address = data['address']
    try:
        crawler = Crawler(address=address, uuid=str(uuid4()))
        crawler.save()
        return Response({'uuid': crawler.uuid})
    except IntegrityError:
        return Response(status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def unregister_crawler(request):
    data = request.DATA
    crawler_uuid = data['uuid']
    try:
        crawler = Crawler.objects.get(uuid=crawler_uuid)
        crawler.delete()
        return Response('Crawler unregistered')
    except Crawler.DoesNotExist:
        return Response('Crawler not found', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def warn_crawler(request):
    data = request.DATA
    crawler_address = data['address']
    try:
        crawler = Crawler.objects.get(address=crawler_address)
        crawler.increase_timeouts()
        return Response('Crawler warned')
    except Crawler.DoesNotExist:
        return Response('Crawler not found', status=status.HTTP_404_NOT_FOUND)


# TODO: is it necessary? maybe keep alive mechanism is enough?
@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def ban_crawler(request):
    data = request.DATA
    crawler_address = data['address']
    try:
        crawler = Crawler.objects.get(address=crawler_address)
        crawler.kill()
        return Response('Crawler banned')
    except Crawler.DoesNotExist:
        return Response('Crawler not found', status=status.HTTP_404_NOT_FOUND)