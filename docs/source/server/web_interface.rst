.. _ServerWebInterface:

fcs.server.web_interface
=======================================

In this module web methods for managing Task Server are defined. These methods are implemented as classes that
contain proper POST and GET methods. Requests are encapsulated in JSON messages.

.. py:class:: index

   Returns diagnostic information about Task Server's efficiency, assigned crawlers 
   and links packages sent to them.

   :return: Diagnostic information.
   :rtype: JSON

.. py:class:: feedback

   Sends user's feedback with rating of crawled data. Required POST parameters are:
   
   * link - rated link
   * rating - rating of the given link
   
   :return: Feedback sending confirmation.
   :rtype: string

.. py:class:: put_data

   Handles crawled data package received from crawler. Required POST parameters are:
   
   * id - crawled data package ID
   * data - crawled data
   
   :return: Confirmation.
   :rtype: string

.. py:class:: stats

   Returns statistics summarise from given time period. Required POST parameters are:
   
   * seconds - number of seconds for which measurement was done (this method returns statistics since (now - seconds)).

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
