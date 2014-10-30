fcs.manager.tasks
=======================================

This module contains the following task-functions:

.. py:function:: notify_about_crawler_data()

   Task-function for Huey plugin. Sends notification about waiting data from crawler. Requires running Redis server.
   
.. py:function:: remove_old_mail_data()

   Task-function for Huey plugin. Removes old email notifications from data base. Requires running Redis server.
