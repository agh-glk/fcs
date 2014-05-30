Module fcs.manager.autoscale_views
=======================================

This module contains methods that handle requests for autoscale module operations. All methods are decorated with Django @api_view decorator.

.. py:function:: register_task_server(request)

   Registers new task server.

   :param request: Request object.

   Required request data parameters are:

   * task_id - ID of task this server is being registered for
   * address - new task server's address


.. py:function:: unregister_task_server(request)

   Unregisters a task server.

   :param request: Request object.

   Required request data parameters are:

   * task_id - ID of task this server is registered for
   * uuid - UUID of task server to unregister


.. py:function:: stop_task(request)

   Stops a task.

   :param request: Request object.

   Required request data parameters are:

   * task_id - ID of task to stop
   * uuid - UUID of server that manages this task


.. py:function:: register_crawler(request)

   Registers new crawler.

   :param request: Request object.

   Required request data parameters are:

   * address - new crawler's address


.. py:function:: unregister_crawler(request)

   Unregisters a crawler.

   :param request: Request object.

   Required request data parameters are:

   * uuid - UUID of crawler to unregister