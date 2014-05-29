Module fcs.manager.api_views
=======================================

api_views module contains methods that handle REST requests for tasks management. All methods are decorated with Django @api_view decorator.

.. py:function:: add_task(request)

   Creates new task.

   :param request: Request object. It must be authenticated with OAuth2 Token. Required request data parameters are:

   * name
   * priority

.. autofunction:: delete_task
.. autofunction:: pause_task
.. autofunction:: resume_task
.. autofunction:: get_data_from_crawler

TEST
