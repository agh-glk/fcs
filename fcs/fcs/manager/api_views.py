from django.core.exceptions import ValidationError
import requests
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from models import Task, QuotaException
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
    *mime_type* - list of MIME types separated by whitespace\n
    *start_links* - list of urls separated by whitespace - starting point of crawling
    *whitelist* - urls (regexp) which should be crawled\n
    *blacklist* - urls (regexp) which should not be crawled\n
    *max_links* - size of task
    """
    data = request.DATA
    user = request.user
    try:
        task = Task.objects.create_task(user=user, name=data['name'], priority=int(data['priority']), expire=data['expire'],
                            start_links = data['start_links'], mime_type=data['mime_type'], whitelist=data['whitelist'],
                            blacklist=data['blacklist'], max_links=int(data['max_links']))
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
    Downloads data gathered by crawler. Request must be authenticated with OAuth2 Token.
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if task.server is None:
        return Response("Cannot download data - task has no running task server!",
                        status=status.HTTP_412_PRECONDITION_FAILED)
    r = requests.get(task.server.address + '/get_data?size=' + str(size))
    return Response(r.content)
