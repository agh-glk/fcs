fcs.server.content_db
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

      :param string url: Crawled page URL.
      :param string links: Links visited during crawling process.
      :param string content: Crawled content to put into database.

   .. py:method:: get_file_with_data_package(size)

      Returns path to file with crawled data of given size.
   
      :param int size: Size of demanded data in MB.
      :return: Path to file with crawled data.
      :rtype: string

   .. py:method:: size()

      Returns the number of elements (i.e. crawled content) in the database (taking into consideration the fact
      that after getting a record via web application or API, it is no longer available).
   
      :return: Number of elements in database.
      :rtype: int

   .. py:method:: added_records_num()

      Returns number of entries containing information about sites that have been crawled since the beginning
      of crawling (takes also into account already unavailable data).

      :return: Number of added entries informing about crawled sites.
      :rtype: int

   .. py:method:: clear()

      Clears content of database and closes it.

   .. py:method:: show()

      Prints entries in database.
