Module fcs.manager.management.commands.autoscaling
=======================================

The autoscaling module. It is run as a Django application command.


.. py:data:: CURRENT_PATH
.. py:data:: PATH_TO_SERVER
.. py:data:: PATH_TO_CRAWLER
.. py:data:: SERVER_SPAWN_TIMEOUT
.. py:data:: MAX_CRAWLERS_NUM
.. py:data:: DEFAULT_LINK_QUEUE_SIZE
.. py:data:: MIN_LINK_PACKAGE_SIZE
.. py:data:: STATS_PERIOD
.. py:data:: MIN_CRAWLER_STATS_PERIOD
.. py:data:: MIN_SERVER_STATS_PERIOD
.. py:data:: AUTOSCALING_PERIOD
.. py:data:: LOOP_PERIOD
.. py:data:: EFFICIENCY_THRESHOLD
.. py:data:: LOWER_LOAD_THRESHOLD
.. py:data:: UPPER_LOAD_THRESHOLD
.. py:data:: INIT_SERVER_PORT
.. py:data:: INIT_CRAWLER_PORT

.. py:class:: Command

   Definition of the command.

   .. py:attribute:: address
   .. py:attribute:: server_port
   .. py:attribute:: crawler_port
   .. py:attribute:: last_scaling
   .. py:attribute:: old_crawlers
   .. py:attribute:: changed

   .. py:method:: handle(*args, **options)

   .. py:method:: print_tasks

   .. py:method:: check_tasks_state

   .. py:method:: check_server_assignment(task)

      :param Task task:

   .. py:method:: handle_priority_changes()

   .. py:method:: spawn_task_server(task)

      :param Task task:

   .. py:method:: spawn_crawler()

   .. py:method:: assign_crawlers_to_servers()

   .. py:method:: autoscale()
