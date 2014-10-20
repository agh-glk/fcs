Module fcs.server.linkdb
=======================================

This module contains implementations of API for link database. Link database stores information about links that
are to visit or have been already visited by Crawling Units.

.. py:class:: BaseLinkDB

   This is a base class for concrete database API implementations.

   .. py:method:: is_in_base(link)

      Checks if the given link is already in database.
   
      :param string link: searched link

   .. py:method:: add_link(link, priority, depth)

      Adds given link to database.
      
      :param string link: link to add
      :param int priority:
      :param int depth:
      :param string fetch_time:

   .. py:method:: get_link()



   .. py:method:: change_link_priority(link, rate)

      :param string link:
      :param int rate:


   .. py:method:: get_details(link)

      Returns additional information about the given link.


   .. py:method:: close()

      Closes database.

   .. py:method:: clear()

      Clears database content.


.. py:class:: GraphAndBTreeDB(base_name, policy_module)

   Implementation of link database API. It is based on the Berkeley DB Btree (`bsddb3 module <https://pypi.python.org/pypi/bsddb3>`_ is used) and on `Neo4j <http://neo4j.com/>`_.

   :param string base_name: Name of the database
   :param AbstractPolicyModule policy_module: describes established policy (how links should be created, how and when priorities should be modified, etc.)

   .. py:attribute:: found_links_db_name
   
      Name of database storing the :py:attr:`found_links` structure.
      
   .. py:attribute:: found_links
   
      Structure with links and crawled content of web sites pointed by these links. This structure is based on the Neo4j graph database.
   
   .. py:attribute:: priority_queue_db_name
   
      Name of database storing the :py:attr:`priority_queue` structure.
   
   .. py:attribute:: priority_queue
   
      Priority queue storing links to be crawled with their priorities. This structure is based on the Berkeley DB Btree.

   .. py:method:: is_in_base(link)

      Checks if the given link is already in database
   
      :param string link: searched link
      :return: information if the link is in database
      :rtype: boolean

   .. py:method:: size()


   .. py:method:: add_link(link, priority, depth, fetch_time="")

      Adds given link to database.
   
      :param string link: link to add
      :param int priority:
      :param int depth:
      :param string fetch_time:

   .. py:method:: get_link()

   .. py:method:: change_link_priority(link, rate)
   
      :param string link:
      :param int rate:

   .. py:method:: get_details()

      Returns additional information about the given link.
   
      :return: List with 3 strings - priority, fetch date (could be an empty string) and depth of crawling tree (method of crawling tree depth calculating depends on the policy - for details see :ref:`CrawlingDepthPolicy`)
      :rtype: list of strings

   .. py:method:: close()

      Closes database.

   .. py:method:: clear()

      Closes and removes database.


