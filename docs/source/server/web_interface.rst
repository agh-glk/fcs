.. _ServerWebInterface:

fcs.server.web_interface
=======================================

In this module web methods for managing Task Server are defined. These methods are implemented as classes that
contain proper POST and GET methods. Requests are encapsulated in JSON messages.

.. py:class:: index

   Returns diagnostic information about Task Server's efficiency and crawlers.

   :return: Diagnostic information.
   :rtype: string

.. py:class:: feedback

   Handles an user's feedback with ratings of crawled data.

   :return: Confirmation.
   :rtype: string

.. py:class:: put_data

   Handles crawled data package.
   
   :return: Confirmation.
   :rtype: string

.. py:class:: stats

   Handles statistics request for specified time period.

   :return: Statistics.
   :rtype: string

.. py:class:: crawlers

   Assigns crawlers to the Task Server.
   
   :return: Confirmation.
   :rtype: string

.. py:class:: speed

   Assigns new Task Server speed as URL per minute.

   :return: Confirmation.
   :rtype: string

.. py:class:: update

   Informs about changes of task's settings (i.a. about its stopping, pausing, change of its priority, etc.).
   
   :return: Confirmation.
   :rtype: string

.. py:class:: stop

   Stops Task Server.

   :return: Confirmation.
   :rtype: string

.. py:class:: get_data

   Gets crawled data.

   :return: File with crawling results.
   :rtype: stream

.. py:class:: alive

   :return: Information if Task Server is alive.
   :rtype: string

.. py:class:: kill

   Kills a Task Server.

   :return: Confirmation.
   :rtype: string
   
.. py:class:: WebServer(address='0.0.0.0', port=8800)

   Wrapper for Task Server’s REST API.

   :param int port: Server's port.
   :param string address: Server's address.
   
   .. py:attribute:: urls
   
      Mapping between URLs and web methods.
      
   .. py:attribute:: app
   
      Server is run as a web application. This attribute is an object representing that web application.
      
   .. py:method:: run()
   
      Runs this server.
      
   .. py:method:: get_host()
   
      Returns server's address with its port.
      
      :return: Server's address with its port in the following format: *address:port*.
      :rtype: string
   
   .. py:method:: stop()
   
      Stops this server.
