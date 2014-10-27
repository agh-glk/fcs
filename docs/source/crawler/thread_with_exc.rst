fcs.crawler.thread_with_exc
=======================================

.. py:class:: ThreadWithExc

   Extending threading.Thread class. Used for terminating crawlers.

   .. py:method:: raise_exec(exec_type)

      Raises exception of specified type in this thread.

      :param class exec_type: Exception class.