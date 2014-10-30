fcs.crawler.mime_content_type
=======================================

.. py:class:: MimeContentType(mime_str)

   Represents MIME type (e.g. image/jpeg, text/`*`).
   
   :param string mime_str: String containing MIME type and subtype (separated by semicolon)

   .. py:attribute:: type

      Main type - before slash.

   .. py:attribute:: subtype

      Subtype - after slash.

   .. py:method:: contains(other_mime)

      Checks if method parameter is a subtype of this MIME type.
      
      :param string other_mime: MIME type to check as a potential subtype of this MIME type.
      :return: Information if method parameter is a subtype of this MIME type.
      :rtype: bool

   .. py:method:: one_of(mime_types)

      Checks if one of the MIME types in parameter collection contains this type.
      
      :param list mime_types: Collection of MIME types.
      :return: Information if one of the MIME types in parameter collection contains this type.
      :rtype: bool

