fcs.crawler.mime_content_type
=======================================

.. py:class:: MimeContentType

   Class represents MIME type (e.g. image/jpeg, text/`*`).

   .. py:attribute:: type

      Main type - before slash.

   .. py:attribute:: subtype

      Subtype - after slash.

   .. py:method:: contains(other_mime)

      Checks if method parameter is subtype of this MIME type.

   .. py:method:: contains(mime_types)

      Checks if one of MIME types in parameter collection contains this type.

