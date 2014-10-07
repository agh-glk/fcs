Module fcs.manager.forms
=======================================

In this module the following Django forms are defined:

.. py:class:: ChangePasswordForm

   Form to change user's password


.. py:class:: EditTaskForm

   Form to change task data


.. py:class:: CreateTaskForm

   Form to create new task

   .. py:attribute:: name

   Task's name

   .. py:attribute:: priority

   Task's priority

   .. py:attribute:: start_links

   Starting point of crawling

   .. py:attribute:: whitelist

   URLs which should be crawled

   .. py:attribute:: blacklist

   URLs which should not be crawled

   .. py:attribute:: max_links

    Maximal amount of links that may be visited while crawling

   .. py:attribute:: expire

   Datetime of task expiration

   .. py:attribute:: mime_type

   List of MIME types


.. py:class:: TaskFilterForm

   Form to filter information about tasks