Module fcs.server.url_processor
=======================================

.. py:class:: URLProcessor

   Processes and corrects URLs retrieved from a web site and delivers other methods operating on web addresses (these methods are used e.g. by crawl depth policy classes).

   .. py:staticmethod:: validate(link, domain=None)

      :param string link:
      :param string domain:

   .. py:staticmethod:: identical_hosts(link_a, link_b)

      :param string link_a:
      :param string link_b:
      :return:
      :rtype: boolean

   .. py:staticmethod:: generate_url_hierarchy(link)

      :param string link:
