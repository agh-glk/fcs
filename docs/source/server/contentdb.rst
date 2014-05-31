Module fcs.server.contentdb
=======================================

This module contains API for connection with database for crawled content.

.. py:class:: BerkeleyContentDB(base_name)

   API for Berkeley DB (http://www.oracle.com/database/berkeley-db/). It uses an interface to the Berkeley DB library
   provided by the bsddb module.

   :param string base_name: Name of the database

   .. py:attribute:: content_db

   Object to access Berkeley DB.

   .. py:method:: add_content(url, links, content)

   Adds crawled content do database.

   :param string url: Base URL
   :param string links: Links visited during crawling process
   :param string content: Crawled content to put into database

   .. py:method:: get_file_with_data_package(size)

   Returns file with crawled data of given size.

   :param int size: Size of demanded data
   :return: File with crawled data
   :rtype: file

   .. py:method:: size()

   Returns current size of database

   :return: Size of database
   :rtype: int

   .. py:method:: added_records_num()

   Returns number of added records

   :return: Number of added records
   :rtype: int

   .. py:method:: clear()

   Clears content of database and closes it

   .. py:method:: show()

   Prints information about database