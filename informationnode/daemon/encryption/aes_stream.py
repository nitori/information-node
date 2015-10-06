
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

'''

import Crypto.Cipher.AES
import Crypto.Util.Counter
from informationnode.daemon.encryption.crypto_stream import \
    CryptoStreamEncryption 
import os
import struct

class SeekableCounter:
    def __init__(self, initial_value_bytes):
        """ @param initial_value initial value, 16 random bytes
        """
        assert(len(initial_value_bytes) == 16)
        self.count = int.from_bytes(initial_value_bytes, 'big')

    def seek(self, block):
        """ Seek to the given 16byte block number. The first block has number
            0, the second 1 etc.
        """
        self.count = block

    def __call__(self):
        """ Return binary string of next counter value. """
        self.count += 1
        return int.to_bytes(self.count, 'big')

class AESinRSAStreamEncryption(CryptoStreamEncryption):
    """ This is an AES stream encryption which can store the relevant data
        for encryption (AES key + IV) in a file encrypted with asymetric RSA.

        It doesn't use GCM, and therefore it does NOT provide authentication.
    """

    def __init__(self):
        """ The specified info path is where the encrypted stream info will be
            loaded from or written to.

            This constructor will also always initialize a new fresh encryption
            stream which you can simply use if you don't intend to load up
            an existing one for decryption.
        """
        super().__init__()

        # generate new AES key:
        self.aes_key = os.urandom(32)

        # generate new counter:
        self.ctr_iv = os.urandom(16)
        
        self.initialize_encryption()

    def initialize_encryption(self):
        super().initialize_encryption()
        self.counter = SeekableCounter(initial_value_bytes=self.ctr_iv)
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
        info_bytes += self.ctr_iv
        info_bytes += self.aes_key
        info_bytes += self.hmac_key

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
            key_enc = f.read(32 + 16 + 64)
        decrypted_info = rsa_private_identity.decrypt(key_enc)
        if len(decrypted_info) != 32 + 16 + 64:
            raise ValueError("AES info has wrong length")

        # extract the info for the counter:
        self.ctr_iv = decrypted_info[:16])
        decrypted_info = decrypted_info[16:]

        # extract aes key:
        self.aes_key = decrypted_info[:32]
        decrypted_info = decrypted_info[32:]

        # extract HMAC key:
        self.hmac_key = decrypted_info[:64]

        self.initialize_encryption()

    def encrypt(self, data):
        super().encrypt(data)
        return self.aes_encryption.encrypt(data)

    def decrypt(self, data):
        super().decrypt(data)
        return self.aes_encryption.decrypt(data)

    def seek_step(self):
        """ The amount of bytes that can be seeked in one step. For example,
            if this returns 8 you may only seek to positions 0, 8, 16, ..
        """
        return 16

    def seek(self, absolute_offset):
        """ Tell the crypto stream that you want to resume decryption not from
            the current position, but instead from the given absolute byte
            offset in the stream.

            Not all crypto streams allow this - check seekable() to make sure
            it does.

            However, seeking to 0 to start over decryption from the beginning
            is always possible.
        """
        if absolute_offset == 0:
            # re-initialize stream to start decryption over from beginning:
            self.offset = 0
            self.initialize_encryption()
            return
        if (absolute_offset % 16) != 0:
            raise ValueError("can only seek in multiples of 16 bytes")
        self.counter.seek(absolute_offset / 16)

