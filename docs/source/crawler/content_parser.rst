fcs.crawler.content_parser
=======================================

This module contains classes responsible for parsing content acquired by Crawling Units.

.. py:class:: ParserProvider

   Provides concrete parser instance.
   
   .. py:attribute:: parsers
   
      Dict in the following format: {content_type, parser_instance}. Stores concrete parser instances for the given content type.

   .. py:staticmethod:: get_parser(content_type)

      Returns parser instance depending on passed content type.

      :param string content_type: Type of content to parse (MIME type).
      :return: Instance of parser that is able to parse a content of given type.
      :rtype: Parser
      :raises Exception: if unknown parser type has been requested.


.. py:class:: Parser

   Superclass for concrete parser implementations.

   .. py:method:: parse(content, url="")

      This method should contain parsing logic.

      :param string content: Content to parse.
      :param string url: URL of base site which content is parsed.

   .. note:: Parser class's parse method is not implemented and should be overwritten.


.. py:class:: TextHtmlParser

   Parses HTML type content and retrieves links (recognized by <a href> and <link href> tags).

   .. py:method:: parse(content, url="")

      Parses HTML page content.

      :param string content: Content to parse.
      :param string url: URL of base site which content is parsed.
      :return: List with 2 elements: the first one is the site's HTML encoded in Base64 format, the second one contains links retrieved from that site.
      :rtype: list
