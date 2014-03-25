

class ContentDB:
    def __init__(self):
        self.db = {}

    def add_content(self, url, links, content):
        self.db[url] = (links, content)

    # TODO: concurrency, remove content method etc.
    def content(self):
        return self.db

    def size(self):
        return len(self.db)

