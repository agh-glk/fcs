fcs.server.data_base_policy_module
=======================================

This module contains implementations of key policies - classes that generate a key with information about the priorities of given links.

.. py:class:: AbstractPolicyModule

   .. py:staticmethod:: generate_key(key, priority)

      :param int key:
      :param int priority:
   
   .. py:staticmethod:: calculate_priority(priority, feedback_rating, depth)
   
      :param int priority:
      :param int feedback_rating:
      :param int depth:
      
   .. py:staticmethod:: get_feedback_propagation_depth()



.. py:class:: SimplePolicyModule

   Implementation of :py:class:`AbstractPolicyModule`.
   
   .. py:attribute:: MIN_PRIORITY
   .. py:attribute:: MAX_PRIORITY
   .. py:attribute:: DEFAULT_PRIORITY
   .. py:attribute:: FEEDBACK_PRIORITY_MAPPING

   .. py:staticmethod:: generate_key(key, priority)

      :param int key:
      :param int priority:
      :return:
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
