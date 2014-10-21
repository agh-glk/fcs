.. _ManagerApiViews:

Module fcs.manager.api_views
=======================================

This module contains methods that handle REST requests for tasks management. All methods are decorated with Django @api_view decorator. These methods are mapped on URLs in :ref:`ManagerApiUrls`.

.. py:function:: add_task(request)

   Creates new task.

   :param request: Request object.

   .. note:: Request must be authenticated with OAuth2 Token.

   Required request data parameters are:

   * name - task's name
   * priority - task's priority
   * expire - datetime of task expiration
   * mime_type - list of MIME types separated by whitespace. This parameter specifies types to be crawled
   * start_links - list of URLs separated by whitespace - starting point of crawling
   * whitelist - URLs which should be crawled
   * blacklist - URLs which should not be crawled
   * max_links - maximal amount of links that may be visited while crawling


.. py:function:: delete_task(request, task_id)

   Deletes a task.

   :param request: Request object.
   :param int task_id: ID of task to be deleted.

   .. note:: Request must be authenticated with OAuth2 Token.


.. py:function:: pause_task(request, task_id)

   Pauses a task.

   :param request: Request object.
   :param int task_id: ID of task to be paused.

   .. note:: Request must be authenticated with OAuth2 Token.


.. py:function:: resume_task(request, task_id)

   Resumes a task.

   :param request: Request object.
   :param int task_id: ID of task to be resumed.

   .. note:: Request must be authenticated with OAuth2 Token.


.. py:function:: get_data_from_crawler(request, task_id, size)

   Download data retrieved by crawler.

   :param request: Request object.
   :param int task_id: ID of task which data is to be downloaded.
   :param int size: Size of requested data
