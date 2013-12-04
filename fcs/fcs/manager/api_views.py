from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response
from models import Task, QuotaException

@permission_classes(permissions.IsAuthenticatedOrReadOnly)
@api_view(['POST'])
def add_task(request):
    """
    Create new task
    """
    data = request.DATA
    user = request.user
    try:
        task = Task.create_task(user=user, name=data['name'], priority=data['priority'], expire=data['expire'],
                            type=data['type'], whitelist=data['whitelist'], blacklist=data['blacklist'],
                            max_links=data['max_links'])
    except KeyError as e:
        return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
    except QuotaException as e:
        return Response(e.message, status=status.HTTP_412_PRECONDITION_FAILED)
    return Response({'id': task.id}, status=status.HTTP_201_CREATED)

@permission_classes(permissions.IsAuthenticatedOrReadOnly)
@api_view(['POST'])
def delete_task(request):
    """
    Finish task
    """
    data = request.DATA
    user = request.user
    try:
        task = Task.objects.filter(id=data['task_id'])[0]
        if user != task.user:
            return Response("User is not owner of this task!", status=status.HTTP_403_FORBIDDEN)
    except KeyError as e:
        return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
    except IndexError:
        return Response("There is no task with specified id!", status=status.HTTP_404_NOT_FOUND)
    task.stop()
    return Response(status=status.HTTP_200_OK)

@permission_classes(permissions.IsAuthenticatedOrReadOnly)
@api_view(['POST'])
def pause_task(request):
    """
    Pause task
    """
    data = request.DATA
    user = request.user
    try:
        task = Task.objects.filter(id=data['task_id'])[0]
        if user != task.user:
            return Response("User is not owner of this task!", status=status.HTTP_403_FORBIDDEN)
    except KeyError as e:
        return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
    except IndexError:
        return Response("There is no task with specified id!", status=status.HTTP_404_NOT_FOUND)
    task.pause()
    return Response(status=status.HTTP_200_OK)

@permission_classes(permissions.IsAuthenticatedOrReadOnly)
@api_view(['POST'])
def resume_task(request):
    """
    Resume task
    """
    data = request.DATA
    user = request.user
    try:
        task = Task.objects.filter(id=data['task_id'])[0]
        if user != task.user:
            return Response("User is not owner of this task!", status=status.HTTP_403_FORBIDDEN)
    except KeyError as e:
        return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
    except IndexError:
        return Response("There is no task with specified id!", status=status.HTTP_404_NOT_FOUND)
    task.resume()
    return Response(status=status.HTTP_200_OK)