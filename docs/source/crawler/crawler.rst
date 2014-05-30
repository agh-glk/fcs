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
   :param string event: Event
   :param int port: Port of this Crawler Unit
   :param string manager_address: Address of Manager module
   :param int max_content_length: Maximal size of content
   :param boolean handle_robots: Flag that informs if Crawler Unit should handle robots.txt

   .. py:attribute:: link_package_queue

   Queue of links to crawl

   .. py:method:: put_into_link_queue(link_package)

   Puts links into queue

   :param string link_package: Links to put into queue

   .. py:method:: add_stats(start_time, end_time, links_num)

   Saves statistics

   :param datetime start_time: Start time of crawling process
   :param datetime ent_time: End time of crawling process
   :param int links_num: Number of crawled links

   .. py:method:: clear_stats()

   Clears statistics

   .. py:method:: get_stats(seconds)

   Returns statistics from given time period

   :param int seconds: Defines time period for which statistics should be returned (this method returns statistics
   since now-seconds)
   :return: Statistics from given time period

   .. py:method:: get_address()

   Returns address of this Crawling Unit

   :return: Crawling Unit address

   .. py:method:: get_state()

   Returns Crawling Unit state

   :return: Crawling Unit state

   .. py:method:: stop()

   Stops Crawling Unit

   .. py:method:: kill()

   Kills Crawling Unit

   .. py:method:: run()

   Runs Crawling Unit
