class BaseKeyPolicyModule(object):

    @staticmethod
    def generate_key(key, priority):
        pass


class SimpleKeyPolicyModule(BaseKeyPolicyModule):

    @staticmethod
    def generate_key(key, priority):
        return "%03d%s" % (999 - priority, key)
