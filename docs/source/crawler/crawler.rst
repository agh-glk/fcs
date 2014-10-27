fcs.crawler.crawler
=======================================

This module contains Crawler Unit implementation.

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
   :param boolean handle_robots: Flag that informs if Crawler Unit should handle robots.txt.

   .. py:attribute:: link_package_queue

      Queue of packages of links to crawl.

   .. py:method:: put_into_link_queue(link_package)

      Puts links package into queue.

      :param string link_package: Package of links to put into queue.

   .. py:method:: get_stats(seconds)

      Returns statistics from given time period.

      :param int seconds: Defines time period for which statistics should be returned (this method returns statistics
   since now).
      :return: Statistics from given time period.

   .. py:method:: get_state()

      Returns Crawling Unit state.

      :return: Crawling Unit state

   .. py:method:: stop()

      Stops Crawling Unit.

   .. py:method:: kill()

      Kills Crawling Unit.

   .. py:method:: run()

      Main Crawling Unit loop.
