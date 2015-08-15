
'''
information-node - an advanced tool for data synchronization
Copyright (C) 2015  information-node Development Team (see AUTHORS.md)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

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

    def set_decryption_private_key(self, target_node_privkey):
        self.privkey = target_node_privkey

    def encrypt(self, data):
         
        return data

    def decrypt(self, data):
        pass

class Item(object):
    def __init__(self, suggested_identifier, content_version=1):
        self.mime_type = "text/plain"
        self.classification = "file"
        self.encryption = None
        self.identifier = None
        self.content_version_id = content_version
        self.contents_finalized = True
        self.creation_time = datetime.datetime.now()
        self.modification_time = datetime.datetime.now()
        self.raw_data = None
        if suggested_identifier != None:  # this is a new item:
            # this should be pretty free of collisions, given the
            # suggested identifier:
            item.identifier = uuid.uuid4() + "-" +\
                hashlib.sha224(suggested_identifier).hexdigest()

            # new item that isn't finalized:
            self.contents_finalized = False
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

    def content_set_chunk(self, chunk_no, value):
        # only allow write access if content hasn't been finalized:
        if self.contents_finalized:
            raise RuntimeError('item has been finalized. open a new one '+\
                'with a newer content version instead.')
        # deal with encryption
        if self.encryption != None:
            #
            pass
        self.raw_chunk_data[chunk_no] = value

    def crop_chunks(self, chunk_amount):
        # only allow write access if content hasn't been finalized:
        if self.contents_finalized:
            raise RuntimeError('item has been finalized. open a new one '+\
                'with a newer content version instead.')
        

    def content_set_from_file(self, file_path):
        # only allow write access if content hasn't been finalized:
        if self.contents_finalized:
            raise RuntimeError('item has been finalized. open a new one '+\
                'with a newer content version instead.')

    def content_set_from_bytes(self, bytes):
        # only allow write access if content hasn't been finalized:
        if self.contents_finalized:
            raise RuntimeError('item has been finalized. open a new one '+\
                'with a newer content version instead.') 

class QueryItems(object):
    def get_by_id(self, identifier):
        """ Get all versions of the item with this identifier. """
        items = []
        


