Module fcs.manager.management.commands.autoscaling
=======================================

The autoscaling module. It is run as a Django application command.


.. py:data:: CURRENT_PATH

   Location of autoscaling module.

.. py:data:: PATH_TO_SERVER

   Path to task server web interface.
   
.. py:data:: PATH_TO_CRAWLER

   Path to crawler web interface.
   
.. py:data:: SERVER_SPAWN_TIMEOUT

   A period of time after which task server is considered to be unable to spawn.
   
.. py:data:: MAX_CRAWLERS_NUM

   Maximal amounts of crawlers.
   
.. py:data:: DEFAULT_LINK_QUEUE_SIZE

   Default amount of links to be parsed by crawler.

.. py:data:: MIN_LINK_PACKAGE_SIZE

   Minimal size of package with links.

.. py:data:: STATS_PERIOD

   Frequency of statistics computing.
   
.. py:data:: MIN_CRAWLER_STATS_PERIOD

   A period during which crawler efficiency is not evaluated.
   
.. py:data:: MIN_SERVER_STATS_PERIOD

   A period during which task server efficiency is not evaluated.
   
.. py:data:: AUTOSCALING_PERIOD

   Frequency of downloading the task servers efficiency statistics.

.. py:data:: LOOP_PERIOD

   A period of idleness between work cycles.
   
.. py:data:: EFFICIENCY_THRESHOLD
.. py:data:: LOWER_LOAD_THRESHOLD
.. py:data:: UPPER_LOAD_THRESHOLD
.. py:data:: INIT_SERVER_PORT
.. py:data:: INIT_CRAWLER_PORT

.. py:class:: Command

   Definition of the command.

   .. py:attribute:: address
   
      Address of this autoscaling module.
   
   .. py:attribute:: server_port
   
      The lowest free number of port for new task server.
   
   .. py:attribute:: crawler_port
   
      The lowest free number of port for new crawler.
   
   .. py:attribute:: last_scaling
   
      Time of last scaling.
   
   .. py:attribute:: old_crawlers
   
      Parameter used for check if some crawlers should not be assigned again.
   
   .. py:attribute:: changed
   
      Parameter used for check if some crawlers should not be assigned again.

   .. py:method:: handle(*args, **options)
   
      Main command method, called when command is run.

   .. py:method:: print_tasks

   .. py:method:: check_tasks_state
   
      Checks if new task server should not be run for any of the tasks (e.g. because some task is new or a previous task server did not start).

   .. py:method:: check_server_assignment(task)
   
      Checks if new task server should not be run for the given task and runs task server if needed (e.g. because this task is new or a previous task server did not start).

      :param Task task: task which could need to have new task server assigned

   .. py:method:: handle_priority_changes()

   .. py:method:: spawn_task_server(task)
   
      Spawns task server for the given task. This method is called in two cases: the task is new or previously assigned task server did not confirm its proper launch.

      :param Task task: task for which new task server is spawned

   .. py:method:: spawn_crawler()

   .. py:method:: assign_crawlers_to_servers()

   .. py:method:: autoscale()
