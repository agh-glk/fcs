class BaseKeyPolicyModule(object):

    @staticmethod
    def generate_key(key, priority):
        pass

    @staticmethod
    def comparison_function(key1, key2):
        pass


class SimpleKeyPolicyModule(BaseKeyPolicyModule):

    @staticmethod
    def generate_key(key, priority):
        return "%03d%s" % (999 - priority, key)

    @staticmethod
    def comparison_function(key1, key2):
        if key1 == '' and key2 == '':
            return 0
        return ((key1 < key2) and -1) or ((key1 == key2) and 0) or 1

