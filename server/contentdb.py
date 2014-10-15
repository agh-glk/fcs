import bsddb
import os
import json


class BerkeleyContentDB(object):

    def __init__(self, base_name):
        self.content_db_name = base_name
        self.content_db = bsddb.rnopen(self.content_db_name)
        self.id_iter = 1
        self.get_data_iter = 1
        self.parts_iter = 1

    def add_content(self, url, links, content):
        _json_dict = json.dumps({'url': url, 'links': links, 'content': None})
        try:
            _json_dict = json.dumps({'url': url, 'links': links, 'content': content})
        except Exception as e:
            print "Add content into db exception: %s" % e
        self.content_db[self.id_iter] = _json_dict
        self.id_iter += 1

    def get_file_with_data_package(self, size):
        """
        Size in MB.
        """
        _size = size * 1024 ** 2
        _current_size = 0
        _file = open('part_%s' % self.parts_iter, 'w')
        self.parts_iter += 1
        try:
            while _current_size < _size:
                try:
                    _entry = self.content_db[self.get_data_iter]
                    del self.content_db[self.get_data_iter]
                    self.get_data_iter += 1
                    _current_size += len(_entry)
                    _file.write(_entry)
                except KeyError:
                    return os.path.abspath(_file.name)
            return os.path.abspath(_file.name)
        finally:
            _file.close()

    def size(self):
        return self.id_iter - self.get_data_iter

    def added_records_num(self):
        return self.id_iter

    def clear(self):
        try:
            self.content_db.close()
        except Exception as e:
            print "Remove content db exception: %s" % e
        finally:
            os.remove(self.content_db_name)

    def show(self):
        print self.content_db
