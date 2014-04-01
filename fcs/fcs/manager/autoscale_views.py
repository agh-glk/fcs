from django.db.utils import IntegrityError
import requests
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
        # TODO: validate address and send proper status code
        server = TaskServer(address=server_address)
        server.save()
        task.server = server
        task.save()
        return Response({'whitelist': task.whitelist, 'blacklist': task.blacklist, 'priority': task.priority,
                            'max_links': task.max_links, 'crawling_type': 0, 'active': task.active,
                            'finished': task.finished, 'query': '', "expire_date": str(task.expire_date)})
                            # TODO: change query, crawling type values
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
    try:
        task = Task.objects.get(id=task_id)
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
        crawler = Crawler(address=address)
        crawler.save()
        return Response({'crawler_id': crawler.id})
    except IntegrityError:
        return Response(status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def unregister_crawler(request):
    data = request.DATA
    crawler_id = int(data['crawler_id'])
    try:
        crawler = Crawler.objects.get(id=crawler_id)
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


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def ban_crawler(request):
    data = request.DATA
    crawler_address = data['address']
    try:
        crawler = Crawler.objects.get(address=crawler_address)
        try:
            requests.post(crawler_address + '/kill')
        finally:
            crawler.delete()
        return Response('Crawler banned')
    except Crawler.DoesNotExist:
        return Response('Crawler not found', status=status.HTTP_404_NOT_FOUND)