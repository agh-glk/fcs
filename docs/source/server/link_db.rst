Module fcs.server.link_db
=======================================

This module contains implementations of API for link database. Link database stores information about links that are to be visited or have been already visited by Crawling Units.

.. py:class:: BaseLinkDB

   This is a base class for concrete database API implementations.

   .. py:method:: is_in_base(link)

      Checks if the given link is already in database.
   
      :param string link: searched link

   .. py:method:: add_link(link, priority, depth)

      Adds a link to database.
      
      :param string link: link to add
      :param int priority: link's priority
      :param int depth: 

   .. py:method:: get_link()

      Returns a link to crawl.

   .. py:method:: change_link_priority(link, rate)
   
      Changes link priority.

      :param string link: link which priority has to be changed
      :param int rate: user's link rating. This value is the base of new priority computing.

   .. py:method:: get_details(link)

      Returns details about the given link.
      
      :param string link: link which details have to be given

   .. py:method:: close()

      Closes database.

   .. py:method:: clear()

      Clears database content.


.. py:class:: GraphAndBTreeDB(base_name, policy_module)

   Implementation of link database API. It is based on the Berkeley DB Btree (`bsddb3 module <https://pypi.python.org/pypi/bsddb3>`_ is used) and on `Neo4j <http://neo4j.com/>`_.

   :param string base_name: Name of the database
   :param AbstractPolicyModule policy_module: describes established policy (how links should be created, how and when priorities should be modified, etc.)

   .. py:attribute:: FOUND_LINKS_DB
   
      Name of database storing the :py:attr:`found_links` structure.
   
   .. py:attribute:: priority_queue_db_name
   
      Name of database storing the :py:attr:`priority_queue` structure.
      
   .. py:attribute:: found_links
   
      Structure with links and crawled content of web sites pointed by these links. This structure is based on the Neo4j graph database. Instance of :py:class:`GraphDB`.
   
   .. py:attribute:: priority_queue
   
      Priority queue storing links to be crawled with their priorities. This structure is based on the Berkeley DB Btree.

   .. py:method:: is_in_base(link)

      Checks if the given link is already in database
   
      :param string link: searched link
      :return: information if the link is in database
      :rtype: bool

   .. py:method:: add_link(link, priority, depth)

      Adds given link to database.
      
      :param string link: link to be added
      :param int priority: link's priority
      :param int depth:

   .. py:method:: get_link()
   
      Returns a link to be processed (one with the highest priority).
      
      :return: link to be processed
      :rtype: string

   .. py:method:: change_link_priority(link, rate)
      
      Changes link priority.

      :param string link: link which priority has to be changed
      :param int rate: user's link rating. This value is the base of new priority computing.

   .. py:method:: get_details()

      Returns additional information about the given link.
   
      :return: List with 3 strings - priority, fetch date (could be an empty string) and depth of crawling tree (method of crawling tree depth calculating depends on the policy - for details see :ref:`CrawlingDepthPolicy`)
      :rtype: list
      
   .. py:method:: points(url_a, url_b)
   
   .. py:method:: feedback(link, feedback_rating)
   
      Processes link rating provided in user's feedback.
      
      :param string link: link this feedback concerns
      :param int feedback_rating: link rating provided in the feedback

   .. py:method:: size()

      Number of elements in the priority queue stoting links to be crawled.
      
      :return: number of elements in the queue with links
      :rtype: int

   .. py:method:: close()

      Closes database.

   .. py:method:: clear()

      Closes and removes database.
