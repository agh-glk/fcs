fcs.manager.views
=======================================

This module contains FCS Manager application views rendered in web browser.

.. py:function:: index(request)

   Main page.

   :param django.http.HttpRequest request: The request object used to generate the response.
   :return: HTML code of the page.
   :rtype: django.http.HttpResponse
   

.. py:function:: list_tasks(request)

   List of all current user's tasks.
   
   .. note:: View accessible for logged in users only.

   :param django.http.HttpRequest request: The request object used to generate the response.
   :return: HTML code of the page.
   :rtype: django.http.HttpResponse
   
   
.. py:function:: add_task(request)

   View for creating new task.
   
   .. note:: View accessible for logged in users only.

   :param django.http.HttpRequest request: The request object used to generate the response.
   :return: HTML code of the page.
   :rtype: django.http.HttpResponse
   
   
.. py:function:: show_task(request, task_id)

   Allows pausing, stopping, resuming task and sending feedback. Shows its details. Additionally, some parameters of running or paused task can be changed.

   .. note:: View accessible for logged in users only.
   
   :param django.http.HttpRequest request: The request object used to generate the response.
   :param int task_id: ID of the given task.
   :return: HTML code of the page.
   :rtype: django.http.HttpResponse
   

.. py:function:: send_feedback(request, task_id)

   View for sending user's feedback on crawling results.
   
   .. note:: View accessible for logged in users only.

   :param django.http.HttpRequest request: The request object used to generate the response.
   :param int task_id: ID of the given task.
   :return: redirect to :py:func:`show_task`.
   :rtype: django.http.HttpResponseRedirect
   
   
.. py:function:: api_keys(request)

   Shows Application Key and Secret Key for REST API.
   
   .. note:: View accessible for logged in users only.

   :param django.http.HttpRequest request: The request object used to generate the response.
   :return: HTML code of the page.
   :rtype: django.http.HttpResponse
   
   
.. py:function:: pause_task(request, task_id)

   Pauses task and redirect to tasks list.
   
   .. note:: View accessible for logged in users only.

   :param django.http.HttpRequest request: The request object used to generate the response.
   :param int task_id: ID of the given task.
   :return: Redirect to :py:func:`list_tasks`
   :rtype: django.http.HttpResponseRedirect


.. py:function:: resume_task(request, task_id)

   Resumes task and redirect to tasks list.
   
   .. note:: View accessible for logged in users only.

   :param django.http.HttpRequest request: The request object used to generate the response.
   :param int task_id: ID of the given task.
   :return: Redirect to :py:func:`list_tasks`.
   :rtype: django.http.HttpResponseRedirect
   
   
.. py:function:: stop_task(request, task_id)

   Stops task and redirect to tasks list.
   
   .. note:: View accessible for logged in users only.

   :param django.http.HttpRequest request: The request object used to generate the response.
   :param int task_id: ID of the given task.
   :return: Redirect to :py:func:`list_tasks`.
   :rtype: django.http.HttpResponseRedirect
   

.. py:function:: get_data(request, task_id, size)

   Downloads data gathered by crawler.
   
   .. note:: View accessible for logged in users only.

   :param django.http.HttpRequest request: The request object used to generate the response.
   :param int task_id: ID of the given task related to data to be downloaded.
   :param int size: Size of data to be downloaded in MB.
   :return: Response with data or information about absence of an appropriate task server.
   

.. py:function:: show_quota(request)

   Shows limitations for tasks, described by Quota object.
   
   .. note:: View accessible for logged in users only.

   :param django.http.HttpRequest request: The request object used to generate the response.
   :return: HTML code of the page.
   :rtype: django.http.HttpResponse
   
   
.. py:function:: api_docs_resources(request)

   Swagger view generating REST API documentation.

   :param django.http.HttpRequest request: The request object used to generate the response.
   :return: HTML code of the page and an HttpResponse object with rendered text.
   :rtype: django.http.HttpResponse
   
   
.. py:function:: api_docs_declaration(request, path)

   Swagger view generating REST API documentation located at the given path.

   :param django.http.HttpRequest request: The request object used to generate the response.
   :param string path: Path to documentation.
   :return: HTML code of the page and an HttpResponse object with rendered text.
   :rtype: django.http.HttpResponse
