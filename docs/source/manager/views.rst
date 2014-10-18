Module fcs.manager.views
=======================================

This module contains fcs.manager application views rendered in web browser.

.. py:function:: index(request)

   Main page.

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
   :return: redirect to :py:func:`show_task`
   
   
.. py:function:: api_keys(request)

   Shows Application Key and Secret Key for REST API.

   :param request request: the request object used to generate the response
   :return: HTML code of the page
   
   
.. py:function:: pause_task(request, task_id)

   View for pausing task.

   :param request request: the request object used to generate the response
   :param int task_id: ID of the given task 
   :return: redirect to :py:func:`list_tasks`


.. py:function:: resume_task(request, task_id)

   View for resuming task.

   :param request request: the request object used to generate the response
   :param int task_id: ID of the given task 
   :return: redirect to :py:func:`list_tasks`
   
   
.. py:function:: stop_task(request, task_id)

   View for stopping task.

   :param request request: the request object used to generate the response
   :param int task_id: ID of the given task 
   :return: redirect to :py:func:`list_tasks`
   

.. py:function:: get_data(request, task_id, size)

   View for downloading data gathered by crawler.

   :param request request: the request object used to generate the response
   :param int task_id: ID of the given task related to data to be downloaded
   :param int size: size of data to be downloaded
   :return: response with data or information about absence of an appropriate task server
   

.. py:function:: show_quota(request)

   Shows limitations for tasks, described by Quota object.

   :param request request: the request object used to generate the response
   :return: HTML code of the page
   
   
.. py:function:: api_docs_resources(request)

   Swagger view generating REST API documentation.

   :param request request: the request object used to generate the response
   :return: HTML code of the page and an HttpResponse object with rendered text
   
   
.. py:function:: api_docs_declaration(request, path)

   Swagger view generating REST API documentation located at the given path.

   :param request request: the request object used to generate the response
   :param string path: path of documentation
   :return: HTML code of the page and an HttpResponse object with rendered text
