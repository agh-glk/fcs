Module fcs.server.task_server
=======================================

This module contains implementation of Task Server.


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

   :param string web_server:
   :param int task_id:
   :param string manager_address:
   :param int max_url_depth:

   .. py:attribute:: link_db
   .. py:attribute:: content_db
   .. py:attribute:: crawlers
   .. py:attribute:: max_links
   .. py:attribute:: expire_date
   .. py:attribute:: mime_type
   .. py:attribute:: uuid

   Task Server's UUID

   .. py:attribute:: whitelist
   .. py:attribute:: blacklist
   .. py:attribute:: urls_per_min
   .. py:attribute:: package_cache
   .. py:attribute:: package_id
   .. py:attribute:: processing_crawlers
   .. py:attribute:: status
   .. py:attribute:: crawled_links
   .. py:attribute:: stats_reset_time

   .. py:method:: assign_crawlers(assignment)

   Sets actual crawler assignment. Task Server can send crawling requests only to these crawlers and size
   of packages must be specified in assignment dict for each crawler. It allows to control crawling
   efficiency of all Task Servers.

   :param list of crawlers assignment: Crawler assignment

   .. py:method:: assign_speed(speed)

    Sets Task Server's crawling speed. After each speed change statistics are reset.

    :param int speed: Crawling speed

    .. py:method:: get_address()

    Returns the Task Server's address.

    :return: Task Server's address
    :rtype: string

    .. py:method:: update(data)

    Updates crawling parameters and status. It is usually called when some changes in task data are made using GUI or API.

    :param string data:

    .. py:method:: pause()

    Pauses the Task Server if it was running.

    .. py:method:: resume()

    Resumes the Task Server if it was paused.

    .. py:method:: stop()

    Stops the Task Server. Stopped Task Server won't send crawling requests anymore. It will wait WAIT_FOR_DOWNLOAD_TIME
    seconds for user to download gathered data.

    .. py:method:: kill()

    Kills the Task Server. Task Server that is to be killed, will be stopped as soon as possible.

    .. py:method:: run()

    Runs the Task Server.

    :raises ConnectionError:

    .. py:method:: get_idle_crawlers()

    Returns list of crawlers which are not processing any requests.

    :return: List of idle Crawler Units.
    :rtype: list of crawlers

    .. py:method:: feedback(regex, rate)

    .. py:method:: add_links(links, priority, depth=0, source_url="")

    .. py:method:: readd_links(links)

    .. py:method:: put_data(package_id, data)

     Handles data package received from crawler and puts it into a content database. If received package
     is not in a package cache or crawling request has timed out, no data will be stored in database. It also
     marks crawler which was assigned to this crawling request as 'idle', so next request can be sent to this crawler.

    :param int package_id:
    :param string data:

    .. py:method:: get_data(size)

    Returns crawling result data of given size.

    :param int size: Size of demanded crawling result

    :return: Path to file with crawling results.
    :rtype: string