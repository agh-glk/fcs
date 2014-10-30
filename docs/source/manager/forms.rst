fcs.manager.forms
=======================================

In this module the following Django forms are defined:

.. py:class:: ChangePasswordForm

   Form for changing user's password.


.. py:class:: EditTaskForm

   Form for changing task data.


.. py:class:: CreateTaskForm(user)

   Form for creating new task.
   
   :param User user: Task's owner

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

   .. py:attribute:: expire

      Datetime of task expiration.

   .. py:attribute:: mime_type

      MIME types which are to be crawled.


.. py:class:: SendFeedbackForm

   Form for sending feedback (URLs rating).


.. py:class:: TaskFilterForm

   Form for filtering information about tasks.
