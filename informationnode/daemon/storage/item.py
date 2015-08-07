
import datetime
import hashlib
import json
import uuid

class PasswordEncryption(object):
    def __init__(self, password_pubkey_path, password_privkey_path):
        self.password_pubkey_path = password_pubkey_file
        self.password_privkey_path = password_privkey_file

class TargetNodeEncryption(object):
    def __init__(self, target_node_pubkey):
        self.target_node_pubkey = target_node_pubkey
        self.privkey = None

    def set_decryption_key(self, target_node_privkey):
        self.privkey = target_node_privkey

    def encrypt(self, data):
         
        return data

    def decrypt(self, data):
        pass

class Item(object):
    CHUNK_SIZE=(1024 * 1000)
    def __init__(self, suggested_identifier):
        self.mime_type = "text/plain"
        self.classification = "file"
        self.encryption = None
        self.identifier = None
        self.creation_time = datetime.datetime.now()
        self.raw_chunk_data = None
        if suggested_identifier != None:
            # this should be pretty free of collisions, given the
            # suggested identifier:
            item.identifier = uuid.uuid4() + "-" +\
                hashlib.sha224(suggested_identifier).hexdigest()
        return item

    def save(self):
        if self.raw_chunk_data == None or self.identifier == None:
            raise RuntimeError("this is not a proper item with "+\
                "content - did you use Item.create_from_content?")
        raise RuntimeError("needs storage driver implementation")

    def _refresh_contents(self):
        raise RuntimeError("needs storage driver implementation")

    def unlock_encryption_with_password(self, password):
        return

    def lock_encryption(self):
        return

    def ensure_target_node_encryption_aes_key(self):
        pass 


    def content_chunk_count(self):
        return 0

    def content_get(self, chunk_no):
        return None

    def content_set(self, chunk_no, value):
        if self.encryption != None:
            #
            pass
        self.raw_chunk_data[chunk_no] = value

