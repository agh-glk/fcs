import threading
import bsddb
import uuid
import os
import json


class ContentDB:
    def __init__(self):
        self.lock = threading.RLock()
        self.db = {}

    def add_content(self, url, links, content):
        self.lock.acquire()
        self.db[url] = (links, content)
        self.lock.release()

    def content(self):
        return self.db

    def size(self):
        return len(self.db)

    def get_data_package(self, size):
        self.lock.acquire()
        keys = self.db.keys()[:size]
        data = []
        for key in keys:
            data.append([key, self.db[key][0]])
            # TODO: uncomment following line; line above is only for testing purposes
            #data.append([key, self.db[key][0], self.db[key][1]])
            del self.db[key]
        self.lock.release()
        return data


class BerkeleyContentDB(object):
    CONTENT_DB = 'content_db'

    def __init__(self, base_name):
        self.content_db_name = base_name + self.__class__.CONTENT_DB + str(uuid.uuid4())
        self.content_db = bsddb.rnopen(self.content_db_name)
        self.id_iter = 1
        self.get_data_iter = 1
        self.parts_iter = 1

    def add_content(self, url, links, content):
        _json_dict = json.dumps({'url': url, 'links': links, 'content': None})
        try:
            _json_dict = json.dumps({'url': url, 'links': links, 'content': content})
        except:
            raise
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
                    print _current_size
                    _file.write(_entry)
                except KeyError:
                    return os.path.abspath(_file.name)
            return os.path.abspath(_file.name)
        finally:
            _file.close()

    def size(self):
        return self.id_iter - self.get_data_iter

    def clear(self):
        self.content_db.close()
        os.remove(self.content_db_name)

    def show(self):
        print self.content_db

if __name__ == '__main__':
    db = BerkeleyContentDB("aa")
    for i in range(100000):
        db.add_content('http://ala.pl', ['http://onet.pl', 'http://wp.pl'], "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    print 'F'
    db.get_file_with_data_package(1)
    #db.show()
    #print db.content_db[1]
    db.clear()
