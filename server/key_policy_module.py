class BaseKeyPolicyModule(object):

    @staticmethod
    def generate_key(key, priority):
        pass


class SimpleKeyPolicyModule(BaseKeyPolicyModule):

    MAX_PRIORITY = 999

    @staticmethod
    def generate_key(key, priority):
        return "%03d%s" % (SimpleKeyPolicyModule.MAX_PRIORITY - priority, key)
