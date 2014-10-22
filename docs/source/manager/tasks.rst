fcs.manager.tasks
=======================================

.. py:function:: notify_about_crawler_data()

   Task-function for Huey plugin. Sends notification about waiting data from crawler. Requires running Redis server.
   
.. py:function:: remove_old_mail_data()

   Task-function for Huey plugin. Removes old email notifications from DB. Requires running Redis server.
