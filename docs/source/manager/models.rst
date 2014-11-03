fcs.manager.models
=======================================

This module contains model layer - implementation of system units and consists of object-relational mapping classes:

.. py:class:: UserManager

   Provides methods for creation of user and his Quota or superuser.

   .. py:method:: create_user(username, email, password)

      Creates common FCS user with a default Quota.

      :param string username: New user's name.
      :param string email: New user's email address.
      :param string password: New user's password.
      :return: New user

   .. py:method:: create_superuser(username, email, password)

      Creates FCS superuser that can use admin panel.

      :param string username: New user's name.
      :param string email: New user's email address.
      :param string password: New user's password.
      :return: New superuser


.. py:class:: User

   FCS user class. Extends :py:class:`django.contrib.auth.models.AbstractUser`.

   .. note:: Username, password and email are required. Other fields are optional.

.. py:class:: Quota

   Represents limitations in creating tasks. Each :py:class:`User` object is connected with his personal quota.

   .. py:attribute:: max_priority

      Maximal allowed sum of tasks' priorities.

   .. py:attribute:: max_tasks

      Maximal allowed number of running tasks.

   .. py:attribute:: link_pool

      Maximal allowed sum of tasks' processed links number.

   .. py:attribute:: max_links

      Maximal allowed number of processed links per task.

   .. py:attribute:: urls_per_min

      Expected crawling speed sum. Used by efficiency estimation module and autoscaling.

   .. py:attribute:: user

      Quota's owner.
      
      
.. py:class:: QuotaException

   Raised when user exceeds limitations defined by Quota object.


.. py:class:: TaskManager

   Manages creation of Task.

   .. py:staticmethod:: create_task(user, name, priority, expire, start_links, whitelist='*', blacklist='', max_links=1000, mime_type='text/html')
   
      Returns new task.
      
      :param string user: User's name.
      :param string name: New task's name.
      :param int priority: Task priority.
      :param datetime expire: Task expiration date.
      :param string start_links: List of pages where crawler starts his work.
      :param string whitelist: Allowed URLs as regexp list.
      :param string blacklist: Disallowed URLs as regexp list.
      :param string max_links: Maximal allowed number of processed pages.
      :param string mime_type: List of allowed MIME types.
      :return: New task
      :rtype: Task
      :raises QuotaException: if user quota is exceeded.

.. py:class:: Crawler

   Represents Crawling Unit.

   .. py:attribute:: address

      Crawling unit's address.

   .. py:attribute:: uuid

      Crawling unit's UUID.

   .. py:method:: is_alive()

      Checks if crawler responds for requests.
      
      :return: Information if crawler is alive
      :rtype: bool

   .. py:method:: stop()

      Sends stop request to crawler.

      .. note:: If crawler doesn't respond this object will be deleted.

   .. py:method:: kill()

      Sends kill request to crawler.

      .. note:: If crawler doesn't respond this object will be deleted.

   .. py:method:: send(path, method='get', data=None)

      Sends request to crawler.

      :param string path: Request name, may be one of the following: '/put_links', '/kill', '/stop', '/alive', '/stats'.
      :param string method: Method of request, acceptable values are 'get' or 'post'.
      :param dict data: Dict with parameters (in JSON). Details of particular request's parameters are described in :ref:`CrawlerWebInterface` documentation.
      :return: Response or `None` if connection cannot be established
      :rtype: requests.Response or None


.. py:class:: TaskServer

   Represents server which executes crawling tasks.

   .. py:attribute:: address

      Task Server's address.

   .. py:attribute:: urls_per_min

      Tasks server's speed.

   .. py:attribute:: uuid

      Task Server's UUID.

   .. py:method:: is_alive()

      Checks if Task Server responds for requests.
      
      :return: Information if Task Server is alive
      :rtype: bool

   .. py:method:: kill()

      Sends kill request to Task Server.

      .. note:: If server doesn't respond this object will be deleted.

   .. py:method:: send(self, path, method='get', data=None)

      Sends request to Task Server.

      :param string path: Request name, may be one of the following: '/put_links', '/kill', '/stop', '/alive', '/stats'.
      :param string method: Method of request, acceptable values are 'get' or 'post'.
      :param dict data: Dict with parameters (in JSON). Details of particular request's parameters are described in :ref:`ServerWebInterface` documentation.
      :return: Response or `None` if connection cannot be established
      :rtype: requests.Response or None

   .. py:method:: delete()

      Deletes this Task Server.


.. py:class:: Task

   Represents crawling task defined by user.

   .. py:attribute:: user
   
      User that owns this task.
   
   .. py:attribute:: name
   
      Task's name.
   
   .. py:attribute:: priority
   
      Task's priority.
   
   .. py:attribute:: start_links
   
      Starting point of crawling.
   
   .. py:attribute:: whitelist
   
      URLs which should be crawled (in regex format).
   
   .. py:attribute:: blacklist
   
      URLs which should not be crawled (in regex format).
   
   .. py:attribute:: max_links
   
      Maximal amount of links that may be visited while crawling.
   
   .. py:attribute:: expire_date
   
      Datetime of task expiration.
   
   .. py:attribute:: mime_type
   
      MIME types which are to be crawled.
   
   .. py:attribute:: active

      Boolean value. If true task is running, else task is paused.

   .. py:attribute:: finished

      Boolean value. If true task is finished, else running or paused.

   .. py:attribute:: created
   
      Datetime of task creation.
   
   .. py:attribute:: last_data_download
   
      Time of last crawled data collection.
   
   .. py:attribute:: server
   
      Task Server that handles this task.
   
   .. py:attribute:: last_server_spawn
   
      Time of last spawn of server which was run for handling this task.

   .. py:attribute:: autoscale_change
   
      Boolean value, informs if some task's parameter has been modified. It value is true, Task Server has to be informed of this change. 

   .. py:method:: clean()

      Cleans task's data. Validates new task's fields before save operation.
      
      :raises ValidationError: If task's parameters cannot be validated
      :raises QuotaException: If user's quota has been exceeded

   .. py:method:: save(*args, **kwargs)

      Saves task in data base and sends information about modifications to its Task Server.

   .. py:method:: get_parsed_whitelist()

      Returns whitelist converted from user-friendly regex to python regex.
      
      :return: Whitelist in python regex format
      :rtype: list

   .. py:method:: get_parsed_blacklist()

      Returns blacklist converted from user-friendly regex to python regex.
      
      :return: Blacklist in python regex format
      :rtype: list

   .. py:method:: change_priority(priority)

      Sets task priority.

      .. note:: Task with higher priority crawls more links at the same time than those with lower priority.
      
      :param int priority: Task's new priority.
      :raises QuotaException: if task priority exceeds quota of user which owns this task

   .. py:method:: pause()

      Pauses task.

      .. note::  Paused task does not crawl any links until it is resumed. It temporarily releases resources used by this task (such as priority).

   .. py:method:: resume()

      Resumes task - task becomes active so it can crawl links.
      
      :raises QuotaException: if user has not enough free priority resources to run this task. Then, user should decrease priority of this or other active task.

   .. py:method:: stop()

      Marks task as finished.

      .. note:: Finished tasks cannot be resumed and they do not count to user max_tasks quota. After some time its Task Server will be closed and crawling results will be lost.

   .. py:method:: is_waiting_for_server()

      Checks if running task has no Task Server assigned. This case includes waiting until new Task Server starts.
      
      :return: Information if this task has no Task Server assigned
      :rtype: bool

   .. py:method:: feedback(link, rating)

      Processes feedback from client in order to update crawling process to satisfy client expectations.

      :param string link: Rated link
      :param string rating: Rating as number in range 1 - 5

   .. py:method:: send_update_to_task_server()
   
      Sends information about task update to its Task Server.


.. py:function:: create_api_keys(sender, **kwargs)

   Creates Application object, required for working with REST API.

   :param string sender: signal sender. In our case this parameter is irrelevant, however more details about this mechanism can be found in `Django documentation <https://docs.djangoproject.com/en/dev/topics/signals/>`_.

.. py:class:: MailSent

   Representation of mail sent to user, reminding him to collect crawling data waiting for him.

   .. py:attribute:: tasks
   
      List of tasks related to uncollected data.

   .. py:attribute:: date
   
      Date of mail sending.
