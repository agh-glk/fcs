

class MimeContentType(object):
    wildcard = '*'

    def __init__(self, mime_str):
        _mime_str = mime_str.split(';')[0].split('/')
        _type = _mime_str[0]
        if _type is self.__class__.wildcard:
            _type = ''
        self.type = _type
        if len(_mime_str) < 2 or _mime_str[1] is '*':
            _subtype = ''
        else:
            _subtype = _mime_str[1]
        self.subtype = _subtype

    def __str__(self):
        return "%s/%s" % (self.type, self.subtype)

    def contains(self, other_mime):
        if self.type == "" or other_mime.type == "":
            return True
        if self.type != other_mime.type:
            return False
        if self.subtype == "" or other_mime.subtype == "":
            return True
        if self.subtype == other_mime.subtype:
            return True
        return False

    def one_of(self, mime_types):
        for mime_type in mime_types:
            if mime_type.contains(self):
                return True
        return False

