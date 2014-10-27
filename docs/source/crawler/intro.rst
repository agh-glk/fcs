Crawling Unit module (fcs.crawler)
=======================================

The fcs.crawler module contains classes that implement the Crawling Unit. Crawling Units execute clients' tasks.
Each Crawling Unit receives from a Task Server a pool of URI to fetch. A single Crawling Unit can perform simultaneously
several crawling tasks. Crawling results and other information (like errors), are returned to a Task Server.

:doc:`content_parser`

:doc:`crawler`

:doc:`web_interface`
