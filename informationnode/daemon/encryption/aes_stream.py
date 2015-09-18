
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

import Crypto.Cipher.AES
import Crypto.Util.Counter
from informationnode.daemon.encryption.crypto_stream import \
    CryptoStreamEncryption 
import os
import struct

class AESinRSAStreamEncryption(CryptoStreamEncryption):
    """ This is an AES stream encryption which can store the relevant data
        for encryption (AES key + IV) in a file encrypted with asymetric RSA.
    """

    def __init__(self):
        """ The specified info path is where the encrypted stream info will be
            loaded from or written to.

            This constructor will also always initialize a new fresh encryption
            stream which you can simply use if you don't intend to load up
            an existing one for decryption.
        """

        # generate new AES key:
        self.aes_key = os.urandom(32)

        # generate new counter:
        self.ctr_iv = struct.unpack("=Q", os.urandom(8))[0]
        self.counter = Crypto.Util.Counter.new(128, initial_value=self.ctr_iv)
        
        self.initialize_encryption()

    def initialize_encryption(self):
        self.aes_encryption = Crypto.Cipher.AES.new(self.aes_key,
            Crypto.Cipher.AES.MODE_CTR, counter=self.counter)

    def save_encrypted_info(self, rsa_public_identity, path):
        """ Save the encrypted AES key + CTR IV to a file where it can be
            loaded from again (but only read by someone with the RSA private
            key corresponding to the specified public key).
            
            If the file with the AES info cannot be written, this will raise
            an OSError as usual. (same for reading the RSA key file)
        """

        # collect all the required data as bytes:
        info_bytes = b""
        info_bytes += struct.pack("!Q", os.urandom(8))[0]
        info_bytes += self.aes_key

        # encrypt it with RSA:
        info_bytes_encrypted = rsa_public_identity.encrypt(info_bytes)

        # write it to file:
        with open(path, "wb") as f:
            f.write(info_bytes_encrypted)

    def load_encrypted_info(self, rsa_private_identity, path):
        """ Load the encrypted AES key + CTR IV again. The specified private
            key must be the corresponding one to the public key used
            previously to encrypt it.

            If decryption fails, this will raise a ValueError which indicates
            that the private key was wrong.

            If the file with the AES info cannot be opened, this will raise
            an OSError as usual. (same for the RSA key file)
        """
        
        # decrypt AES key + counter info:
        with open(path, "rb") as f:
            key_enc = f.read(256)  # upper estimate: read 256bit key + iv
        decrypted_info = rsa_private_identity.decrypt(key_enc)
        if len(decrypted_info) != 32 + 8:
            raise ValueError("AES info has wrong length")

        # extract the info for the counter:
        self.ctr_iv = struct.unpack("!Q", decrypted_info[:8])[0]
        self.counter = Crypto.Util.Counter.new(128, initial_value=self.ctr_iv)

        # extract aes key:
        self.aes_key = decrypted_info[8:]

        self.initialize_encryption()

    def encrypt(self, data):
        return self.aes_encryption.encrypt(data)

    def decrypt(self, data):
        return self.aes_encryption.decrypt(data)



