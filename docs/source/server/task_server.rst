fcs.server.task_server
=======================================

This module contains implementation of Task Server.


.. py:data:: URL_PACKAGE_TIMEOUT

   After specified time in seconds package is considered lost.

.. py:data:: DATE_FORMAT

   Datetime format used in system.

.. py:data:: WAIT_FOR_DOWNLOAD_TIME

   Time in seconds tells how long task server waits for downloading crawling results before quit.

.. py:data:: KEEP_STATS_SECONDS

   After this time in seconds old statistics are removed.

.. py:data:: CHECK_EFFICIENCY_PERIOD

   Time in second for which efficiency statistics are gathered.


.. py:class:: Status

   Stores attributes defining Crawler Unit state.

   .. py:attribute:: INIT

      Task Server is being initialized.

   .. py:attribute:: STARTING

      Task Server is starting.

   .. py:attribute:: RUNNING

      Task Server is running.

   .. py:attribute:: PAUSED

      Task Server is paused.

   .. py:attribute:: STOPPING

      Task Server is being stopped.

   .. py:attribute:: KILLED

      Task Server is killed.


.. py:class:: TaskServer(web_server, task_id, manager_address, max_url_depth=1)

   Main class of Task Server, containing its logic.

   :param fcs.server.web_interface.WebServer web_server: Web application class responsible for communication.
   :param int task_id: Id of task for which Task Server is dedicated.
   :param string manager_address: FCS manager module address.
   :param int max_url_depth: Maximal allowed crawling tree depth.

   .. py:attribute:: link_db

      Database for extracted links. Current implementation: :class:`GraphAndBTreeDB`.

   .. py:attribute:: content_db

      Database for content extracted from processed pages. Current implementation:
      :class:`BerkeleyContentDB`.

   .. py:attribute:: crawlers
   
      Dict of the following format: key - Crawling Unit's address, value - links to be processed by this
      Crawling Unit.
   
   .. py:attribute:: max_links
   
      Maximal amount of unique links that may be crawled during the current task.
   
   .. py:attribute:: expire_date
   
      Expiration date of the given task.
   
   .. py:attribute:: mime_type

      List of page allowed MIME types.

   .. py:attribute:: uuid

      Task Server's UUID.

   .. py:attribute:: whitelist

      Regexp with allowed URL form.

   .. py:attribute:: blacklist

      Regexp with forbidden URL form.

   .. py:attribute:: urls_per_min

      Expected efficiency in URLs per minute.

   .. py:attribute:: package_cache
   
      Dict of the following format: key - :py:attr:`package_id`, value - information about packages
      with links that have been sent to Crawling Unit (time of sending, list of links, Crawling Unit's address,
      timeout flag).
   
   .. py:attribute:: package_id
   
      ID of package with links.
   
   .. py:attribute:: processing_crawlers

      List of working crawlers.

   .. py:attribute:: status

      Crawler state, described by :class:`Status`.

   .. py:attribute:: crawled_links

      List for statistics - processed links, crawling beginning and end times.

   .. py:attribute:: stats_reset_time
   
      Object used for computing time period from which the server efficiency statistics are collected.

   .. py:method:: assign_crawlers(assignment)

      Sets actual crawler assignment. Task Server can send crawling requests only to these crawlers and size
      of packages must be specified in assignment dict for each crawler. It allows to control crawling
      efficiency of all Task Servers.

      :param dict assignment: Dict of the following format: key - Crawling Unit's address, value - links
         to be processed by the given Crawling Unit.

   .. py:method:: assign_speed(speed)

      Sets Task Server's crawling speed. After each speed change statistics are reset.

      :param int speed: Crawling speed computed as follows:
        *speed = urls_per_min * task.priority / priority_sum*,
        where *urls_per_min* is defined on the basis of user's quota, *task.priority* is a value of priority
        of the given task and *priority_sum* is a sum of all of the user's tasks priorities.

   .. py:method:: update(data)

      Updates crawling parameters and status. It is usually called when some changes in task data are made
      using GUI or API.

      :param dict data: Task description (parameters of the task).

   .. py:method:: pause()

      Pauses the Task Server if it was running.

   .. py:method:: resume()

      Resumes the Task Server if it was paused.

   .. py:method:: stop()

      Stops the Task Server. Stopped Task Server won't send crawling requests anymore. It will wait
      WAIT_FOR_DOWNLOAD_TIME seconds for user to download gathered data.

   .. py:method:: kill()

      Kills the Task Server. Task Server that is to be killed, will be stopped as soon as possible.

   .. py:method:: run()

      Main Task Server loop.

   .. py:method:: get_idle_crawlers()

      Returns list of crawlers which are not processing any requests.

      :return: List of idle Crawler Units.
      :rtype: list of crawlers

   .. py:method:: feedback(link, rating)
   
      Increases priority of specified link and its children.
      
      :param string link: Link.
      :param string rating: Link's new rating, can be a number 1-5 casted to string.

   .. py:method:: add_links(links, priority, depth=0, source_url="")
   
      Adds links to process.
      
      :param list links: List of links (links are of string type).
      :param int priority: Links' priority, can be a number 0-999 (0 is the lowest priority).
      :param int depth: Depth of crawling for a page from which links have been retrieved.
      :param string source_url: URL of page from which links have been retrieved.
      :raises Exception: in case of an error in database.

   .. py:method:: put_data(package_id, data)

      Handles crawled data package received from crawler and puts it into a content database. If received package
      is not in a package cache or crawling request has timed out, no data will be stored in database. It also
      marks crawler which was assigned to this crawling request as 'idle', so next request can be sent to this crawler.

      :param int package_id: ID of crawled data package (identical to the package ID from crawling request).
      :param string data: Crawled data package.

   .. py:method:: get_data(size)

      Returns path to file with crawling results.

      :param int size: Size of package with demanded crawling results.

      :return: Path to file with crawling results.
      :rtype: string
