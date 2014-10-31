fcs.crawler.crawler
=======================================

This module contains Crawler Unit implementation.

.. py:data:: KEEP_STATS_SECONDS

   After this time in seconds old statistics are removed.
   

.. py:class:: CrawlerState

   Stores attributes defining Crawler Unit states.

   .. py:attribute:: UNDEFINED

    Crawler Unit's state is undefined.

   .. py:attribute:: WORKING

    Crawler Unit is working.

   .. py:attribute:: WAITING

    Crawler Unit is idle.

   .. py:attribute:: CLOSING

    Crawler Unit is being closed.


.. py:class:: Crawler(web_server, event, port, manager_address, max_content_length=1024 * 1024, handle_robots=False)

   Crawler Unit implementation.

   :param string web_server: Object that represents Crawler Unit, used for communication with Task Server.
   :param string event: Instance of threading.Event class used for synchronization at the end of Crawler Unit's work.
   :param int port: Port of this Crawler Unit.
   :param string manager_address: Address of Manager module.
   :param int max_content_length: Maximal size of content.
   :param bool handle_robots: Flag that informs if Crawler Unit should handle robots.txt.

   .. py:attribute:: link_package_queue

      Queue of packages of links to crawl. Each package contains: package ID, links to crawl, Task Server's (i.e. package sender) address, MIME type of data to crawl.
      
   .. py:attribute:: browser
   
   .. py:attribute:: uuid
   
      Crawler Unit's UUID.
      
   .. py:attribute:: stats_reset_time
   
      Object used for computing time period from which the crawler efficiency statistics are collected.
      
   .. py:attribute:: crawled_links
   
      List of tuples with statistics regarding processed links (number of processed links and time crawling these links took).

   .. py:method:: put_into_link_queue(link_package)

      Puts links package into queue.

      :param list link_package: Package of links to put into queue. Each package is a list containing the following information: package ID, links to crawl, Task Server's (i.e. package sender) address, MIME type of data to crawl.

   .. py:method:: get_stats(seconds)

      Returns statistics from given time period.

      :param int seconds: Defines time period for which statistics should be returned (this method returns statistics since (now - seconds)).
      :return: Statistics from given time period (number of crawled links and total time crawling these links took).
      :rtype: dict
      
   .. py:method:: get_address()
   
      Returns this Crawling Unit's full address (with port number)
      
      :return: Crawling Unit's address
      :rtype: string

   .. py:method:: get_state()

      Returns Crawling Unit state.

      :return: Crawling Unit state
      :rtype: :py:class:`CrawlerState`

   .. py:method:: stop()

      Stops Crawling Unit.

   .. py:method:: kill()

      Kills Crawling Unit.

   .. py:method:: run()

      Main Crawling Unit loop.
