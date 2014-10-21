.. _CrawlingDepthPolicy:

Module fcs.server.crawling_depth_policy
=======================================

In this module policies of crawling depth computing are contained.

.. py:class:: BaseCrawlingDepthPolicy

   This is a base class for concrete crawling depth policy implementations.

   .. py:staticmethod:: calculate_depth()

   Returns crawling depth.

   :return: Crawling depth
   :rtype: int


.. py:class:: IgnoreDepthPolicy


.. py:class:: SimpleCrawlingDepthPolicy

   .. py:staticmethod:: calculate_depth(link=None, source_url=None, depth=None)

   :param string link:
   :param string source_url:
   :param int depth:
   :return: Crawling depth
   :rtype: int
   :raises ValueError:


.. py:class:: RealDepthCrawlingDepthPolicy

   .. py:staticmethod:: calculate_depth(link=None, link_db=None)

   :param string link:
   :param string link_db:
   :return: Crawling depth
   :rtype: int
   :raises ValueError:

