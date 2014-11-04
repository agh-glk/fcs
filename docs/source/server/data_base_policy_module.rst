fcs.server.data_base_policy_module
=======================================

This module describes Task Server's behavior during link database key generation and application of user's feedback.

.. py:class:: AbstractPolicyModule

   .. py:staticmethod:: generate_key(key, priority)

      Generates a key with information about the priorities of given links.

      :param int key: Page URL.
      :param int priority: Page priority.
   
   .. py:staticmethod:: calculate_priority(priority, feedback_rating, depth)

      Calculates new priority of page according to rating sent in user's feedback.
   
      :param int priority: Current page priority.
      :param int feedback_rating: Rating sent by user in feedback.
      :param int depth: Page depth in comparison with original site affected by feedback.
      
   .. py:staticmethod:: get_feedback_propagation_depth()

      Returns maximal depth of feedback propagation - how many levels of pages retrieved from original page can have its priority changed.



.. py:class:: SimplePolicyModule

   Implementation of :py:class:`AbstractPolicyModule`.
   
   .. py:attribute:: MIN_PRIORITY
   
      Minimal link priority.
      
   .. py:attribute:: MAX_PRIORITY
   
      Maximal link priority.
      
   .. py:attribute:: DEFAULT_PRIORITY
   
      Default link priority.
      
   .. py:attribute:: FEEDBACK_PRIORITY_MAPPING
   
      Dict with mapping between link rating sent in feedback and its priority.

   .. py:staticmethod:: generate_key(key, priority)
   
      Generates a key with information about the priorities of given links.

      :param int key: Page URL.
      :param int priority: Page priority.
      :return: Link database key.
      :rtype: string

   .. py:staticmethod:: get_feedback_propagation_depth()
   
      :return:
      :rtype: int
      
   .. py:staticmethod:: calculate_priority(priority, feedback_rating, depth)
   
      :param int priority:
      :param int feedback_rating:
      :param int depth:
      :return:
      :rtype: int
