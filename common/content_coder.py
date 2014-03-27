class Base64ContentCoder(object):

    BASE_64 = 'base64'

    @staticmethod
    def encode(content):
        return content.encode(Base64ContentCoder.BASE_64)

    @staticmethod
    def decode(content):
        return content.decode(Base64ContentCoder.BASE_64)