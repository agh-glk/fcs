Module fcs.server.web_interface
=======================================

In this module web methods for managing Task Server are defined. These methods are implemented as classes that
contain proper POST and GET methods. Request are encapsulated in JSON messages.

.. py:class:: index

.. py:class:: feedback

   Sends an user's feedback with ratings of crawled data.

.. py:class:: put_data

.. py:class:: stats

.. py:class:: crawlers

.. py:class:: speed

.. py:class:: update

.. py:class:: stop

   :return: Confirmation of stopping the Task Server
   :rtype: string

.. py:class:: get_data

   Gets crawled data.

.. py:class:: alive

   :return: Information if Task Server is alive
   :rtype: string

.. py:class:: kill

   Kills a Task Server

   :return: Confirmation of killing the Task Server
   :rtype: string