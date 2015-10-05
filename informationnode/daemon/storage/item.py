
'''
information-node - an advanced tool for data synchronization
Copyright (C) 2015  Information Node Development Team (see AUTHORS.md)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


In addition, as a special exception, the copyright holders give
  permission to link the code of portions of this program with the
  OpenSSL library under certain conditions as described in each
  individual source file, and distribute linked combinations
  including the two.
You must obey the GNU General Public License in all respects
  for all of the code used other than OpenSSL.  If you modify
  file(s) with this exception, you may extend this exception to your
  version of the file(s), but you are not obligated to do so.  If you
  do not wish to do so, delete this exception statement from your
  version.  If you delete this exception statement from all source
  files in the program, then also delete it here.

'''

import datetime
import hashlib
import json
import os
import struct
import uuid

from informationnode.daemon.storage import ItemChunkManager 

class Item(object):
    """ This item structure is the base for all user data stored in an
        information node.

        Each item maps to a folder in the node's storage directory. In there,
        it has a separate subfolder for each content_version, where the actual
        data, encryption details etc are stored.

        Use a QueryItems instance to manage those items.
    """
    CHUNK_SIZE=(1024 * 100)
    def __init__(self, suggested_identifier, \
            encryption=None, content_version=1):
        self.mime_type = "text/plain"
        self.classification = "file"
        self.encryption = encryption
        self.identifier = None
        self.content_version_id = content_version
        self.contents_finalized = True
        self.creation_time = datetime.datetime.now()
        self.modification_time = datetime.datetime.now()
        self.raw_data = None
        self.raw_chunk_data = dict()
        self.chunk_count = 0

        if suggested_identifier != None:  # this is a new item:
            # this should be pretty free of collisions, given the
            # suggested identifier:
            self.identifier = uuid.uuid4() + "-" +\
                hashlib.sha224(suggested_identifier).hexdigest()

            # new item that isn't finalized:
            self.contents_finalized = False
        else: # initialize item from disk
            pass

        self.item_chunk_manager = ItemChunkManager(\
            self.CHUNK_SIZE, self.identifier, self.encryption,
            content_version=self.content_version_id)
        self.item_chunk_manager.contents_finalized = self.contents_finalized 

    def save(self):
        if self.raw_chunk_data == None or self.identifier == None:
            raise RuntimeError("this is not a proper item with "+\
                "content - did you use Item.create_from_content?")
        raise RuntimeError("needs storage driver implementation")

    def _refresh_contents(self):
        raise RuntimeError("needs storage driver implementation")

    def unlock_encryption_with_password(self, password):
        """ Required for password-protected items to read or modify them.
            When the item is initially created it will be unlocked, but
            otherwise unlocking is required for any sort of access.
        """
        self.encryption.unlock(password)

    def unlock_encryption_with_identity(self, identity):
        """ Unlock the item contents with the given RSA identity if it was
            encrypted for a specific target node.

            Returns ValueError if unlocking failed.
        """
        self.encryption.set_decryption_by_identity(identity)

    def lock_encryption(self):
        """ If encryption was enabled and unlocked for this item, the password
            and/or crypto data will be forgotten again. Unless you unlock, the
            item can neither be read nor modified.
        """
        self.encryption.lock()

    def open(self):
        """ Return a file-like object to read and write on this item.
        """
        return


