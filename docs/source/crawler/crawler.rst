Module fcs.crawler.crawler
=======================================

This module contains Crawler Unit implementation.

.. py:class:: CrawlerState

   Stores attributes defining Crawler Unit states.

   .. py:attribute:: UNDEFINED

   Crawler Unit's state is undefined
   .. py:attribute:: WORKING

   Crawler Unit is working

   .. py:attribute:: WAITING

   Crawler Unit is idle

   .. py:attribute:: CLOSING

   Crawler Unit is being closed


.. py:class:: Crawler(web_server, event, port, manager_address, max_content_length=1024 * 1024, handle_robots=False)

   Crawler Unit implementation.

   :param string web_server: Web Server