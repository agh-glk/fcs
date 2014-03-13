

class ContentDB:
    def __init__(self):
        self.db = {}

    def add_content(self, url, links, content):
        self.db[url] = (links, content)

    # TODO: remove
    def content(self):
        return self.db

