from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from models import Task
from django.contrib.auth.models import User

@api_view(['POST'])
def add_task(request):
    """
    Create new task
    """
    data = request.DATA
    user = User.objects.filter(id=data['id'])[0]
    task = Task.create_task(user=user, name=data['name'], priority=data['priority'], expire=data['expire'],
                            type=data['type'], whitelist=data['whitelist'], blacklist=data['blacklist'],
                            max_links=data['max_links'])
    return Response({'id': task.id}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def delete_task(request):
    """
    Finish task
    """
    data = request.DATA
    task = Task.objects.filter(id=data['task_id'])[0]
    task.stop()
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def pause_task(request):
    """
    Pause task
    """
    data = request.DATA
    task = Task.objects.filter(id=data['task_id'])[0]
    task.pause()
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def resume_task(request):
    """
    Resume task
    """
    data = request.DATA
    task = Task.objects.filter(id=data['task_id'])[0]
    task.resume()
    return Response(status=status.HTTP_200_OK)