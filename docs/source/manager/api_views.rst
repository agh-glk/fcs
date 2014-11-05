.. _ManagerApiViews:

fcs.manager.api_views
=======================================

This module contains methods that handle REST requests for tasks management. All methods are decorated
with Django REST framework @api_view decorator. These methods are mapped on URLs in :ref:`ManagerApiUrls` module.

.. py:function:: add_task(request)

   Creates new task. Handles REST request for task creation. Required POST parameters:
   
   * name - name of task
   * priority - task priority
   * expire - datetime of task expiration
   * mime_type - list of MIME types separated by whitespace
   * start_links - list of urls separated by whitespace - starting point of crawling
   * whitelist - URLs (regexp) which should be crawled
   * blacklist - URLs (regexp) which should not be crawled
   * max_links - size of task

   :param rest_framework.Request request: Request object.

   .. note:: Request must be authenticated with OAuth2 Token.
   
   :return: Response with new task's ID if successful, response with error message and code otherwise.
   :rtype: rest_framework.response.Response


.. py:function:: delete_task(request, task_id)

   Finishes a task. Handles REST request for task finish. Required POST parameters:
   
   * id - task id

   :param rest_framework.Request request: Request object.
   :param int task_id: ID of task to be deleted.

   .. note:: Request must be authenticated with OAuth2 Token.
   
   :return: Response with confirmation if successful, response with error message and code otherwise.
   :rtype: rest_framework.response.Response


.. py:function:: pause_task(request, task_id)

   Pauses a task. Handles REST request for task deactivation. Required POST parameters:
   
   * id - task id

   :param rest_framework.Request request: Request object.
   :param int task_id: ID of task to be paused.

   .. note:: Request must be authenticated with OAuth2 Token.
   
   :return: Response with confirmation if successful, response with error message and code otherwise.
   :rtype: rest_framework.response.Response


.. py:function:: resume_task(request, task_id)

   Resumes a task. Handles REST request for task activation. Required POST parameters:
   
   * id - task id

   :param rest_framework.Request request: Request object.
   :param int task_id: ID of task to be resumed.

   .. note:: Request must be authenticated with OAuth2 Token.
   
   :return: Response with confirmation if successful, response with error message and code otherwise.
   :rtype: rest_framework.response.Response


.. py:function:: get_data_from_crawler(request, task_id, size)

   Downloads data gathered by crawler.

   :param rest_framework.Request request: Request object.
   :param int task_id: ID of task which data is to be downloaded.
   :param int size: Size of requested data.
   
   .. note:: Request must be authenticated with OAuth2 Token.
   
   :return: Response with crawled content if successful, response with error message and code otherwise.
   :rtype: rest_framework.response.Response
