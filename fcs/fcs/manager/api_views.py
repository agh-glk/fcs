from django.core.exceptions import ValidationError
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
    Creates new task.

    Handles REST request for task creation. Request must be authenticated with OAuth2 Token.
    Required POST parameters:\n
    *name* - name of task\n
    *priority* - task priority\n
    *expire* - datetime of task expiration\n
    *types* - list of numbers indicating CrawlingType\n
    *whitelist* - urls which should be crawled first, crawling start point\n
    *blacklist* - urls (regexp) which should not be crawled\n
    *max_links* - size of task
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
    except (QuotaException, ValidationError) as e:
        return Response(e.message, status=status.HTTP_412_PRECONDITION_FAILED)
    except Exception as e:
        return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
    return Response({'id': task.id}, status=status.HTTP_201_CREATED)


@protected_resource()
@api_view(['POST'])
def delete_task(request, task_id):
    """
    Finishes task.

    Handles REST request for task finish. Request must be authenticated with OAuth2 Token.
    Required POST parameters:\n
    *id* - task id
    """
    user = request.user
    try:
        task = Task.objects.get(id=task_id)
        if user != task.user:
            return Response("User is not owner of this task!", status=status.HTTP_403_FORBIDDEN)
    except Task.DoesNotExist:
        return Response("There is no task with specified id!", status=status.HTTP_404_NOT_FOUND)
    task.stop()
    return Response(status=status.HTTP_200_OK)


@protected_resource()
@api_view(['POST'])
def pause_task(request, task_id):
    """
    Pauses task.

    Handles REST request for task deactivation. Request must be authenticated with OAuth2 Token.
    Required POST parameters:\n
    *id* - task id
    """
    user = request.user
    try:
        task = Task.objects.get(id=task_id)
        if user != task.user:
            return Response("User is not owner of this task!", status=status.HTTP_403_FORBIDDEN)
        task.pause()
    except Task.DoesNotExist:
        return Response("There is no task with specified id!", status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_200_OK)


@protected_resource()
@api_view(['POST'])
def resume_task(request, task_id):
    """
    Resumes task.

    Handles REST request for task activation. Request must be authenticated with OAuth2 Token.
    Required POST parameters:\n
    *id* - task id
    """
    user = request.user
    try:
        task = Task.objects.get(id=task_id)
        if user != task.user:
            return Response("User is not owner of this task!", status=status.HTTP_403_FORBIDDEN)
        task.resume()
    except (QuotaException, ValidationError) as e:
        return Response(e.message, status=status.HTTP_412_PRECONDITION_FAILED)
    except Task.DoesNotExist:
        return Response("There is no task with specified id!", status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_200_OK)


@protected_resource()
@api_view(['POST'])
def get_data_from_crawler(request, task_id, size):
    """
    Downloads data gathered by crawler.
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
