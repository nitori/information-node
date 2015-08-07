
class PasswordEncryption(object):
    def __init__(self, password_file):
        self.password_file = password_file

class 

class Entry(object):
    def __init__(self):
        self.content = dict()
        self.mime_type = "text/plain"
        self.classification = "file"
        self.encryption = None
