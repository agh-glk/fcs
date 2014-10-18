Module fcs.manager.views
=======================================

This module contains fcs.manager application views rendered in web browser.

.. py:function:: index(request)

   Main page

   :param request request: the request object used to generate the response
   :return: HTML code of the page
   

.. py:function:: list_tasks(request)

   List of all current user's tasks.

   :param request request: the request object used to generate the response
   :return: HTML code of the page
   
   
.. py:function:: add_task(request)

   View for creating new task.

   :param request request: the request object used to generate the response
   :return: HTML code of the page
   
   
.. py:function:: show_task(request, task_id)

   Allows pausing, stopping and resuming task. Shows its details. Additionally, parameters of running or paused task can be changed.

   :param request request: the request object used to generate the response
   :param int task_id: ID of the given task 
   :return: HTML code of the page
   

.. py:function:: send_feedback(request, task_id)

   View for sending user's feedback on crawling results.

   :param request request: the request object used to generate the response
   :param int task_id: ID of the given task 
   :return: Redirect to :py:func:`show_task`
   
   
.. py:function:: api_keys(request)

   Shows Application Key and Secret Key for REST API.

   :param request request: the request object used to generate the response
   :return: HTML code of the page
   
   
.. py:function:: pause_task(request, task_id)

   View for pausing task

   :param request request: the request object used to generate the response
   :param int task_id: ID of the given task 
   :return: Redirect to :py:func:`list_tasks`
