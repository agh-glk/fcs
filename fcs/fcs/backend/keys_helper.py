import uuid


class KeysHelper():

    @classmethod
    def generate(cls):
        return str(uuid.uuid4())
