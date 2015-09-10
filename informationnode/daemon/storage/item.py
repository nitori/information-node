
'''
information-node - an advanced tool for data synchronization
Copyright (C) 2015  Information Node Development Team (see AUTHORS.md)

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

from informationnode.daemon.identity import Identity

class PasswordEncryption(object):
    """ This is a password encryption which uses a pub/private RSSA key pair
        which is specified to secure an AES stream for item encryption.

        What does this class do in detail:

        Usually, an RSA identity would be used for each separate password used
        (shared among all items that are encrypted with this password), and
        the private key would be stored encrypted with the given password.

        This structure just handles AES with the given identity - you need to
        handle storing the RSA identity (including the required private key
        encryption with the password) elsewhere.

        TODO: document where the RSA identities for pw encryption are handled
    """
    def __init__(self, password_rsa_path,\
            password, aes_info_path=None):
        self.password_pubkey_path = password_pubkey_file
        self.password_privkey_path = password_privkey_file

        # get AES key:
        if aes_info_path != None:
            with open(aes_info_path, "rb") as f:
                key_enc = f.read(256)  # read 256bit key + info
            identity = Identity(password_rsa_path)
            decrypted_info = identity.decrypt(key_enc)
            if len(decrypted_info != 32):
                raise ValueError("AES key info has wrong length")
            
        else:
            # generate new AES key:
            self.aes_key = os.urandom(32)

    def save_encrypted_aes_info(self, path):
        pass

class TargetNodeEncryption(object):
    """ This handles asymmetric encryption for another information node's
        public RSA identity information which must be provided.

        It will then encrypt an AES stream which can only be opened with the
        target node's information key (unless one day RSA is broken of
        course).
    """
    def __init__(self, target_node_pubkey, aes_info_path=None):
        self.target_node_pubkey = target_node_pubkey
        self.privkey = None
        self.aes_info_path = aes_info_path

        # generate new AES key:
        self.aes_key = os.urandom(32)

    def save_encrypted_aes_info(self, path):
        pass

    def set_decryption_private_key(self, target_node_privkey,
            passphrase=None):
        self.privkey = target_node_privkey
        with open(self.aes_info_path, "rb") as f:
            key_enc = f.read(256)  # read 256bit key + info
        identity = Identity(target_node_privkey, passphrase=passphrase)
        decrypted_info = identity.decrypt(key_enc)
        if len(decrypted_info != 32):
            raise ValueError("AES key has wrong length")

    def encrypt(self, data):
        
        return data

    def decrypt(self, data):
        pass

class ItemChunk(object):
    def __init__(self, item, no):
        self.item = item
        self.no = no
        self.on_disk = False

    def transfer_to_disk(self):
        """ Transfer the chunk data from memory to disk.
        """
        if self.on_disk:
            return
        self.on_disk = True
        del(self.data)

    def transfer_from_disk(self):
        """ Load chunk data from disk.
        """
        if not self.on_disk:
            return
        self.on_disk = False

    def delete_data(self):
        """ Delete this chunk's data, including from disk if any.
        """
        raise RuntimeError("not implemented yet")

    def size(self):
        """ Size of the data contained in thus chunk, or None if not currently
            known.
        """
        return None

    def set_data(self, value):
        if self.on_disk:
            self.on_disk = False
        self.data = value

    def get_data(self):
        return self.data

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
            item.identifier = uuid.uuid4() + "-" +\
                hashlib.sha224(suggested_identifier).hexdigest()

            # new item that isn't finalized:
            self.contents_finalized = False
        else: # initialize item from disk
            pass

        return item

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
        return

    def unlock_encryption_with_identity(self, identity):
        """ Unlock the item contents with the given RSA identity if it was
            encrypted for a specific target node.

            Returns ValueError if unlocking failed.
        """
        return

    def lock_encryption(self):
        """ If encryption was enabled and unlocked for this item, the password
            and/or crypto data will be forgotten again. Unless you unlock, the
            item can neither be read nor modified.
        """
        return

    def ensure_target_node_encryption_aes_key(self):
        pass 

    def content_chunk_count(self):
        return self.chunk_count

    def content_get(self, chunk_no):
        if chunk_no >= self.chunk_count or chunk_no < 0:
            raise ValueError('no chunk with id ' + str(chunk_no))

        # load up chunk if not there:
        if not chunk_no in self.raw_chunk_data:
            self.raw_chunk_data = ItemChunk(self, chunk_no)

        # return data:
        return self.raw_chunk_data[chunk_no].get_data()

    def content_set_chunk(self, chunk_no, data):
        # only allow write access if content hasn't been finalized:
        if self.contents_finalized:
            raise RuntimeError('item has been finalized. open a new one '+\
                'with a newer content version instead.')

        # deal with encryption
        if self.encryption != None:
            #
            pass

        # increase total chunk count if necessary:
        self.chunk_count = max(self.chunk_count, chunk_no - 1)
        if chunk_no in self.raw_chunk_data:
            self.raw_chunk_data[chunk_no].set_data(data)
            return

        # create new chunk:
        chunk = ItemChunk(self, chunk_no)
        chunk.set_data(value)
        self.raw_chunk_data[chunk_no] = chunk

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



