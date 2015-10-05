
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

import os
import struct
import uuid

from informationnode.daemon.encryption.identity import Identity
from informationnode.daemon.encryption.aes_stream import \
    AESinRSAStreamEncryption 

class PasswordEncryption(AESinRSAStreamEncryption):
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
    def __init__(self, load_from_folder_path, password, aes_info_path=None):
        super().__init__()
        self.load_from_folder_path = load_from_folder_path

        # set the proper stored AES key, if this isn't a new encryption:
        if load_from_folder_path != None:
            if password == None:
                # do nothing for now
                return
            self.load_from_folder(load_from_folder_path)
        else:
            self.crypto_identity = Identity()
        self.stored_password = password

    def unlock(self, password):
        self.stored_password = password
        self.load_from_folder(self.load_from_folder_path)

    def lock(self):
        if hasattr(self, "aes_key"):
            del(self.aes_key)
        if hasattr(self, "crypto_identity"):
            del(self.crypto_identity)
        if hasattr(self, "stored_password"):
            del(self.stored_password)

    def save_to_folder(self, path):
        super().save_encrypted_aes_info(self.crypto_identity,
            os.path.join(path, "aes_info.data"))
        self.crypto_identity.save_to_file(
            os.path.join(path, "rsa_identity.data"),
            passphrase=self.stored_password)

    def load_from_folder(self, path, password=None):
        self.crypto_identity = Identity(
            os.path.join(path, "rsa_identity.data"),
            passphrase=password)
        super().load_encrypted_aes_info(self.crypto_identity)

class TargetNodeEncryption(AESinRSAStreamEncryption):
    """ This handles asymmetric encryption for another information node's
        public RSA identity information which must be provided.

        It will then encrypt an AES stream which can only be opened with the
        target node's information key (unless one day RSA is broken of
        course).
    """
    def __init__(self, target_node_pubkey_path):
        super().__init__()
        self.privkey = None

        # construct public key-only identity with supplied key file:
        self.crypto_identity = Identity(target_node_pubkey_path)

        if self.crypto_identity.has_private():
            self.set_decryption_by_identity(self.crypto_identity)

    def set_decryption_private_key(self, target_node_privkey_path,
            passphrase=None):
        """ Provide an RSA private key to allow this to decrypt data.
        """
        identity = Identity(target_node_privkey_path,
            passphrase=passphrase)
        self._set_decryption_by_identity(identity)

    def set_decryption_by_identity(self, identity):
        self.crypto_identity = identity
        super().load_encrypted_aes_info(self.crypto_identity)

    def save_to_folder(self, path):
        super().save_encrypted_aes_info(self.crypto_identity,
            os.path.join(path, "aes_info.data"))

    def load_from_folder(self, path):
        if not self.crypto_identity.has_private():
            raise RuntimeError("no private key provided, cannot decrypt")
        super().load_encrypted_aes_info(self.crypto_identity,
            os.path.join(path, "aes_info.data"))


