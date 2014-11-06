fcs.manager.middleware
=======================================

This module contains the following middleware classes:

.. py:class:: AutoLogout

   Signs out user after certain time of inactivity. This time is specified as AUTO_LOGOUT_DELAY in settings.
   
   .. py:method:: process_request(request)
   
      Checks if user who sent the request was inactive during a time period longer than one specified in AUTO_LOGOUT_DELAY parameter. If yes, logouts this user. Otherwise, updates information about user last activity.
      
      :param django.http.HttpRequest request: User's request.
