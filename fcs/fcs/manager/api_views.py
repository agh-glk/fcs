from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from models import Task, QuotaException, CrawlingType
from oauth2_provider.decorators import protected_resource
from django.shortcuts import get_object_or_404


@protected_resource()
@api_view(['POST'])
def add_task(request):
    """
    Create new task
    """
    data = request.DATA
    user = request.user
    try:
        _crawling_types = CrawlingType.objects.filter(type__in=map(lambda x: int(x), data['types']))
        task = Task.objects.create_task(user=user, name=data['name'], priority=int(data['priority']), expire=data['expire'],
                            types=_crawling_types, whitelist=data['whitelist'], blacklist=data['blacklist'],
                            max_links=int(data['max_links']))
    except KeyError as e:
        return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
    except QuotaException as e:
        return Response(e.message, status=status.HTTP_412_PRECONDITION_FAILED)
    except Exception as e:
        return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
    return Response({'id': task.id}, status=status.HTTP_201_CREATED)


@protected_resource()
@api_view(['POST'])
def delete_task(request, task_id):
    """
    Finish task
    """
    user = request.user
    try:
        task = Task.objects.get(id=task_id)
        if user != task.user:
            return Response("User is not owner of this task!", status=status.HTTP_403_FORBIDDEN)
    except KeyError as e:
        return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
    except Task.DoesNotExist:
        return Response("There is no task with specified id!", status=status.HTTP_404_NOT_FOUND)
    task.stop()
    return Response(status=status.HTTP_200_OK)


@protected_resource()
@api_view(['POST'])
def pause_task(request, task_id):
    """
    Pause task
    """
    user = request.user
    try:
        task = Task.objects.get(id=task_id)
        if user != task.user:
            return Response("User is not owner of this task!", status=status.HTTP_403_FORBIDDEN)
    except KeyError as e:
        return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
    except Task.DoesNotExist:
        return Response("There is no task with specified id!", status=status.HTTP_404_NOT_FOUND)
    task.pause()
    return Response(status=status.HTTP_200_OK)


@protected_resource()
@api_view(['POST'])
def resume_task(request, task_id):
    """
    Resume task
    """
    user = request.user
    try:
        task = Task.objects.get(id=task_id)
        if user != task.user:
            return Response("User is not owner of this task!", status=status.HTTP_403_FORBIDDEN)
    except KeyError as e:
        return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
    except Task.DoesNotExist:
        return Response("There is no task with specified id!", status=status.HTTP_404_NOT_FOUND)
    task.resume()
    return Response(status=status.HTTP_200_OK)


@protected_resource()
@api_view(['POST'])
def get_data_from_crawler(request, task_id, size):
        task = get_object_or_404(Task, id=task_id, user=request.user)
        return Response(status = status.HTTP_200_OK)
