fcs.server.graph_db
=============================

This module describes API for graph database, used by :class:`GraphAndBTreeDB` in :ref:`LinkDB_`.

.. py:class:: GraphDB

   Class provides easy access to Neo4j database.


   .. py:method:: is_in_base(link)

      Checks if the given link is already in database.

      :param string link: Searched link.
      :return: Information if the link is in database.
      :rtype: bool

   .. py:method:: add_link(link, priority, depth)

      Adds given link to database.

      :param string link: URL to add.
      :param int priority: Link priority.
      :param int depth: Link depth.
      :return: Object representing new node in database.
      :rtype: `neo4j.Nodes` if successful, `None` otherwise

   .. py:method:: change_link_priority(link, priority)

      Changes link priority.

      :param string link: URL with priority modified.
      :param int priority: Link's new priority.
      :return: Link's old priority.
      :rtype: int

   .. py:method:: get_details(link)

      Returns information stored in database about specified link.

      :param string link: URL with priority modified.
      :return: List with 3 strings - priority, fetch date(could be empty string) and depth.
      :rtype: list

   .. py:method:: points(url_a, url_b)

      Connects two URLs-representing nodes in graph with relationship: "url_b obtained from page
      identified with url_a".

      :param string url_a: First URL.
      :param string url_b: Second URL.
      :return: Object representing edge between nodes representing `url_a` and `url_b`.
      :rtype: neo4j.Relationships

   .. py:method:: get_connected(links)

      Provides list of URLs which can be extracted from specified pages.

      :param list links: List of strings representing URLs.
      :return: List of URLs (as strings).
      :rtype: list

   .. py:method:: clear()

      Clears database instance.
