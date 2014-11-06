fcs.manager.autoscale_views
=======================================

This module contains methods that handle requests for autoscale module operations. All methods are decorated with Django REST framework @api_view decorator.

.. py:function:: register_task_server(request)

   Registers new Task Server. Required POST parameters are:
   
   * task_id - ID of task new Server is being registered for
   * address - Task Server's address

   :param rest_framework.Request request: Request object.
   :return: Response with task parameters if successful, response with error message and code otherwise
   :rtype: rest_framework.response.Response


.. py:function:: unregister_task_server(request)

   Unregisters a Task Server. Required POST parameters are:

   * task_id - ID of task this Server is registered for
   * uuid - UUID of Task Server to unregister

   :param rest_framework.Request request: Request object.
   :return: Response with confirmation if successful, response with error message and code otherwise
   :rtype: rest_framework.response.Response
   

.. py:function:: stop_task(request)

   Stops a task. Required POST parameters are:

   * task_id - ID of task to stop
   * uuid - UUID of Task Server that manages this task

   :param rest_framework.Request request: Request object.
   :return: Response with confirmation if successful, response with error message and code otherwise
   :rtype: rest_framework.response.Response


.. py:function:: register_crawler(request)

   Registers new Crawling Unit. Required POST parameters are:

   * address - new Crawling Unit's address

   :param rest_framework.Request request: Request object.
   :return: Response with Crawling Unit's UUID if successful, response with error message and code otherwise
   :rtype: rest_framework.response.Response


.. py:function:: unregister_crawler(request)

   Unregisters a Crawling Unit. Required POST parameters are:

   * uuid - UUID of Crawling Unit to unregister

   :param rest_framework.Request request: Request object.
   :return: Response with confirmation if successful, response with error message and code otherwise
   :rtype: rest_framework.response.Response
