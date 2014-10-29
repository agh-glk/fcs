fcs.crawler.thread_with_exc
=======================================

.. py:class:: ThreadWithExc

   Extends threading.Thread class. Used for terminating crawlers.

   .. py:method:: raise_exc(exctype)

      Raises in this thread a specified type of exception.

      :param object exctype: Exception class.
      :raises TypeError: if exctype is an instance, not type (class).
      :raises ValueError: in case of invalid thread ID
      :raises SystemError: if raising exception fails
