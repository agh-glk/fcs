.. _CrawlingDepthPolicy:

fcs.server.crawling_depth_policy
=======================================

In this module crawling depth computing policies are contained.

.. py:class:: BaseCrawlingDepthPolicy

   This is a base class for crawling depth policy implementations.

   .. py:staticmethod:: calculate_depth()

      Returns crawling depth.

      :return: Crawling depth.
      :rtype: int

.. py:class:: IgnoreDepthPolicy

   Implementation that ignores depth. Calculated depth is always 0.

   .. py:staticmethod:: calculate_depth()

      Always returns 0.
   
      :return: Crawling depth (0).
      :rtype: int


.. py:class:: SimpleCrawlingDepthPolicy

   Depth is computed in accordance with the following rules:
   
   \* - new domain
   
   1) A.com -> \*B.com => depth_2 = 0
   
   2) A.com -> A.com/aaa/ => depth_2 = depth_1 + 1
   
   3) A.com -> \*B.com -> A.com/aaa/ => depth_1 = x, depth_2 = 0, depth_3 = 0

   .. py:staticmethod:: calculate_depth(link=None, source_url=None, depth=None)

      :param string link: Address of site for which crawling depth is computed.
      :param string source_url: Address of site from which link has been retrieved.
      :param int depth: *source_url* page depth.
      :return: Crawling depth.
      :rtype: int
      :raises ValueError: if some URL is invalid.


.. py:class:: RealDepthCrawlingDepthPolicy

   Depth is computed in accordance with the following rules:
   
   \* - new domain
   
   1) A.com -> \*B.com => depth_2 = 0
   
   2) A.com -> A.com/aaa/ => depth_2 = depth_1 + 1
   
   3) A.com -> \*B.com -> A.com/aaa/ => depth_1 = x, depth_2 = 0, depth_3 = x + 1

   .. py:staticmethod:: calculate_depth(link=None, link_db=None)

      :param string link: Address of site for which crawling depth is computed
      :param string link_db: Database Access Object, extending `BaseLinkDB`.
      :return: Crawling depth.
      :rtype: int
      :raises ValueError: if some URL is invalid.

