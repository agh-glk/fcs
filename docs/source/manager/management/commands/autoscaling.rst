fcs.manager.management.commands.autoscaling
==============================================

The autoscaling module. It is run as a Django application command.


.. py:data:: CURRENT_PATH

   Location of autoscaling module.

.. py:data:: PATH_TO_SERVER

   Path to Task Server web interface.
   
.. py:data:: PATH_TO_CRAWLER

   Path to crawler web interface.
   
.. py:data:: SERVER_SPAWN_TIMEOUT

   A period of time after which Task Server is considered to be unable to spawn.
   
.. py:data:: MAX_CRAWLERS_NUM

   Maximal amounts of crawlers.
   
.. py:data:: DEFAULT_LINK_QUEUE_SIZE

   Default size of package with links to be parsed by crawler.

.. py:data:: MIN_LINK_PACKAGE_SIZE

   Minimal size of package with links that have to be processed by crawler.

.. py:data:: STATS_PERIOD

   Frequency of statistics computing.
   
.. py:data:: MIN_CRAWLER_STATS_PERIOD

   A period during which crawler efficiency is not evaluated.
   
.. py:data:: MIN_SERVER_STATS_PERIOD

   A period during which Task Server efficiency is not evaluated.
   
.. py:data:: AUTOSCALING_PERIOD

   Frequency of downloading the Task Servers efficiency statistics.

.. py:data:: LOOP_PERIOD

   A period of idleness between work cycles.
   
.. py:data:: EFFICIENCY_THRESHOLD

   Border actual-to-expected efficiency ratio. If its value is lower than actual-to-expected efficiency ratio, no more crawlers will be spawned.

.. py:data:: LOWER_LOAD_THRESHOLD

   If crawlers' actual-to-expected load is higher then this value, new crawler is spawned.

.. py:data:: UPPER_LOAD_THRESHOLD

   If crawlers' actual-to-expected load is lower then this value, one crawler is stopped.

.. py:data:: INIT_SERVER_PORT

   Port number of first Task Server. Each next has one higher.

.. py:data:: INIT_CRAWLER_PORT

   Port number of first Crawling Unit. Each next has one higher.


.. py:function:: sigint_signal_handler(num, stack)

   SIGINT signal handler. Kills all Crawling Units and Task Servers.
   
   :param int num: signal number
   :param frame stack: current stack frame (for details on frame type, see `Python documentation <https://docs.python.org/2/reference/datamodel.html>`_)
   

.. py:class:: Command

   Definition of the command 'autoscaling'.

   .. py:attribute:: address
   
      Address of this autoscaling module.
   
   .. py:attribute:: server_port
   
      The lowest free number of port for new Task Server.
   
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

   .. py:method:: print_tasks()

      Prints tasks' details on standard output (usually console window).

   .. py:method:: check_tasks_state()
   
      Checks if new Task Server should not be run for any of the tasks (e.g. because some task is new or a previous Task Server did not start).

   .. py:method:: check_server_assignment(task)
   
      Checks if new Task Server should not be run for the given task and runs Task Server if needed (e.g. because this task is new or a previous Task Server did not start).

      :param Task task: task which could need to have new Task Server assigned

   .. py:method:: handle_priority_changes()

      If some crawling-speed affecting task parameters change, speed of every crawler is updated.

   .. py:method:: spawn_task_server(task)
   
      Spawns Task Server for the given task. This method is called in two cases: the task is new or previously assigned Task Server did not confirm its proper launch.

      :param Task task: task for which new Task Server is spawned

   .. py:method:: spawn_crawler()

      Spawns new crawler.

   .. py:method:: assign_crawlers_to_servers()

      Sets group of crawlers for every task.

   .. py:method:: autoscale()

      Kills not responding servers and crawlers, calculates efficiency, stops or spawns new crawlers if necessary.
