class AbstractPolicyModule(object):

    @staticmethod
    def generate_key(key, priority):
        pass

    @staticmethod
    def calculate_priority(priority, feedback_rating, depth):
        pass

    @staticmethod
    def get_feedback_propagation_depth():
        pass


class SimplePolicyModule(AbstractPolicyModule):

    MIN_PRIORITY = 0
    MAX_PRIORITY = 999
    DEFAULT_PRIORITY = 500
    FEEDBACK_PRIORITY_MAPPING = {'1': 0.7, '2': 0.9, '3': 1, '4': 1.1, '5': 1.3}

    @staticmethod
    def generate_key(key, priority):
        return str("%03d%s" % (SimplePolicyModule.MAX_PRIORITY - priority, key))

    @staticmethod
    def get_feedback_propagation_depth():
        return 3

    @staticmethod
    def calculate_priority(priority, feedback_rating, depth):
        print priority
        if depth == 0:
            return min(SimplePolicyModule.MAX_PRIORITY, int(int(priority) *
                                                    SimplePolicyModule.FEEDBACK_PRIORITY_MAPPING[feedback_rating]))
        else:
            _delta = (SimplePolicyModule.FEEDBACK_PRIORITY_MAPPING[feedback_rating] - 1) \
                     * (1.0 - (float(depth + 1.0) / (SimplePolicyModule.get_feedback_propagation_depth() + 1)))
            print _delta
            return max(SimplePolicyModule.MIN_PRIORITY,
                       min(SimplePolicyModule.MAX_PRIORITY, int(int(priority) * (1 + _delta))))

