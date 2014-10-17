Module fcs.server.linkdb
=======================================

This module contains implementations of API for link database. Link database stores information about links that
are to visit or have been already visited by Crawling Units.

.. py:class:: BaseLinkDB

   This is a base class for concrete database API implementations.

   .. py:method:: is_in_base(link)

   Checks if the given link is already in database


   .. py:method:: add_link(link, priority, depth)

   Adds given link to database.

   .. py:method:: get_link()



   .. py:method:: change_link_priority(link, rate)




   .. py:method:: get_details(link)

   Returns additional information about the given link.


   .. py:method:: close()

   Closes database.

   .. py:method:: clear()

   Clears database content.


.. py:class:: BerkeleyBTreeLinkDB(base_name, policy_module)

   Implementation of link database API. It is based on the Berkeley DB Btree and uses bsddb3 module.

   :param string base_name: Name of the database
   :param string policy_module:

   .. py:attribute:: found_links_db_name
   .. py:attribute:: self.found_links
   .. py:attribute:: self.priority_queue_db_name
   .. py:attribute:: self.priority_queue

   .. py:method:: is_in_base(link)

   Checks if the given link is already in database

   :param string link: Searched link
   :return: Information if the link is in database
   :rtype: boolean

   .. py:method:: size()


   .. py:method:: add_link(link, priority, depth, fetch_time="")

   Adds given link to database.

   :param string link: Link to add
   :param int priority:
   :param int depth:
   :param string fetch_time:

   .. py:method:: readd_link(link)


   .. py:method:: get_link()

   :raises bsddb.db.DBNotFoundError:

   .. py:method:: change_link_priority(link, rate)

   .. py:method:: get_details()

   Returns additional information about the given link.

   :return: List with 3 strings - priority, fetch date (could be empty string) and depth
   :rtype: list of strings

   .. py:method:: close()

   Closes database.

   .. py:method:: clear()

   Closes and removes database.


