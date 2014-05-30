Module fcs.crawler.content_parser
=======================================

This module contains classes responsible for parsing content acquired by Crawling Units.

.. py:class:: ParserProvider

   Provides concrete parser instance

   .. py:staticmethod:: get_parser(content_type)

   Returns parser instance depending on passed content type.

   :param string content_type: Type of content to parse
   :return: Instance of parser that is able to parse a content of given type


.. py:class:: Parser

   Superclass for concrete parser implementations

   .. py:method:: parse(content, url="")

   This method should contain parsing logic

   :param string content: Content to parse
   :param string url: Base site's URL

   .. note:: Parser class's parse method is not implemented


.. py:class:: TextHtmlParser

   Parses HTML type content and retrieves links (recognized by <a href> and <link href> tags)

   .. py:method:: parse(content, url="")

   This method should contain parsing logic

   :param string content: Content to parse
   :param string url: Base site's URL
   :return: List with passed content and retrieved links