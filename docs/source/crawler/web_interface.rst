.. _CrawlerWebInterface:

fcs.crawler.web_interface
=======================================

In this module web methods for managing Crawling Units are defined. These methods are implemented as classes that contain proper POST or GET methods. Request are encapsulated in JSON messages.

.. py:class:: index

   Shows information about state of the Crawling Unit and its efficiency.
   
   :return: Diagnostic information (crawler's state and efficiency).
   :rtype: string
   

.. py:class:: put_links

   Passes links to crawl to Crawling Unit. Required POST parameters are:
   
   * id - ID of the package with links
   * links - links to crawl
   * server_address - address of Task Server that sent this package of links
   * mime_type - list of MIME types of data to crawl

   :return: Confirmation of sending links to Crawling Unit.
   :rtype: string
   :raises KeyError: if request body is incorrect


.. py:class:: stop

   Stops a Crawling Unit.

   :return: Confirmation of stopping the Crawling Unit.
   :rtype: string


.. py:class:: kill

   Kills a Crawling Unit.

   :return: Confirmation of killing the Crawling Unit.
   :rtype: string


.. py:class:: alive

   Pings if Crawling Unit is alive.

   :return: Information that Crawling Unit is alive.
   :rtype: string


.. py:class:: stats

   Asks Crawling Unit for statistics from a given time period. Reqired POST parameter is:
   
   * seconds - time period for which statistics should be returned (counting since now)

   :return: Crawling statistics from a given time period.
   :rtype: JSON
   
   
.. py:class:: Server(port=8080, address='0.0.0.0')

   Wrapper for Crawler Unit's REST API.
   
   :param int port: Server's port.
   :param string address: Server's address.
   
   .. py:attribute:: urls
   
      Mapping between URLs and web methods.
   
   .. py:attribute:: app
   
      Server is run as a web application. This attribute is an object representing that web application.
   
   .. py:method:: run()
   
      Runs this server.
   
   .. py:method:: kill()
   
      Kills this server.
