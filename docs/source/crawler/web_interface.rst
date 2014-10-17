.. _CrawlerWebInterface:

Module fcs.crawler.web_interface
=======================================

In this module web methods for managing Crawling Units are defined. These methods are implemented as classes that
contain proper POST methods. Request are encapsulated in JSON messages.

.. py:class:: put_links

   Passes links to crawl to Crawling Unit.

   :return: Confirmation of sending links to Crawling Unit
   :rtype: string
   :raises KeyError: If request body is incorrect


.. py:class:: stop

   Stops a Crawling Unit.

   :return: Confirmation of stopping the Crawling Unit
   :rtype: string


.. py:class:: kill

   Kills a Crawling Unit.

   :return: Confirmation of killing the Crawling Unit
   :rtype: string


.. py:class:: alive

   Pings if Crawling Unit is alive.

   :return: Information if Crawling Unit is alive
   :rtype: string


.. py:class:: stats

   Asks Crawling Unit for statistics from a given time period.

   :return: Crawling statistics from a given time period
   :rtype: JSON
