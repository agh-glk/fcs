Task Server module (fcs.server)
=======================================

This module contains implementation of Task Server. Each Task Server is responsible for handling just one task at the
same time. However, it does not mean that one physical machine corresponds with only one Task Server, since this model
is logical. Each Task Server contains its own database for storing links or crawled data.

:doc:`content_db`

:doc:`crawling_depth_policy`

:doc:`data_base_policy_module`

:doc:`graph_db`

:doc:`link_db`

:doc:`task_server`

:doc:`url_processor`

:doc:`web_interface`
