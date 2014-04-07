import threading


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

