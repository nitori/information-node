
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

from Crypto.PublicKey import RSA
from Crypto import Random
import json
import math

class IdentityPublicKey(object):
    def __init__(self, key):
        self.key = key
        if self.key.has_private():
            self.key = self.key.publickey()

    def size(self):
        return self.key.size()   
 
    def save_to_file(self, path):
        f = open(path, "wb")
        f.write(self.key.exportKey('PEM'))
        f.close()

    def encrypt(self, value):
        return self.key.encrypt(value)

class IdentityPrivateKey(object):
    def __init__(self, key):
        self.key = key
        if not self.key.has_private():
            raise ValueError("RSA key has no private key info")

    def size(self):
        return self.key.size()

    def decrypt(self, value):
        return self.key.decrypt(value)

class Identity(object):
    """ A cryptographic RSA identity which can be used for asymmetric
        encryption.
    """
    ENCRYPT_BIT_MINIMUM=(256 * 2)
    def __init__(self, from_file=None, passphrase=None):
        if from_file == None:
            # generate a new pair
            rng = Random.new().read
            key = RSA.generate(4096 * 2, rng)
            self.public_key = IdentityPublicKey(key)
            self.private_key = IdentityPrivateKey(key)
        else:
            # read from file:
            f = open(from_file, "rb")
            contents = f.read(4096 * 1024)  # no more than 4mb
            f.close()
            key = RSA.importKey(contents.decode("utf-8", "ignore"),
                passphrase=passphrase)
            self.public_key = IdentityPublicKey(key)
            if key.has_private():
                self.private_key = IdentityPrivateKey(key)
            else:
                self.private_key = None

            # ensure the minimum required RSA key size is met:
            if self.public_key.size() < ENCRYPT_BIT_MINIMUM or (\
                    self.private_key != None and \
                    self.private_key.size() < ENCRYPT_BIT_MINIMUM):
                self.private_key = None
                self.public_key = None
                raise ValueError("this RSA key doesn't meet the required " +\
                    "minimum bit size for proper encryption")

    def encrypt(self, value):
        """ Encrypt a self.size() bits value with this identity.

            The length must not exceed self.size() bits.
            If you want to encrypt longer values, use this to encrypt an AES
            key instead and use AES to encrypt your actual data stream.

            Returns the encrypted bytes.
        """
        if len(value) > math.floor(self.public_key.size() / 8.0):
            raise ValueError("value is too large to be encrypted with this "+\
                "RSA key")
        return self.public_key.encrypt(value)

    def size(self):
        """ Get the amount of bits that can be encrypted or decrypted with
            this RSA identity.
        """
        if self.private_key != None:
           return min(self.private_key.size(), self.public_key.size())
        return self.public_key.size()

    def decrypt(self, value):
        """ Decrypt a maximum <length> bit long value with this identity.

            This can only be done if this identity contains the private key
            part (which means it cannot be just instantiated from the pure
            public information).

            Returns the decrypted bytes, or raises a ValueError if decryption
            failed.
        """
        if len(value) > math.floor(self.public_key.size() / 8.0):
            raise ValueError("value is too large to be encrypted with this "+\
                "RSA key")
        return self.private_key.decrypt(value)

    def save_to_file(self, path, passphrase=None):
        """ Save the identity to a file. Please note this includes the
            sensitive private key if self.private_key != None.

            It will be encrypted with the given passphrase.
        """
        if self.private_key == None:
            raise RuntimeError("cannot save a full identity without " +\
                "private key information")
        f = open(path, "wb")
        if passphrase == None:
            f.write(self.private_key.key.exportKey(pkcs=8))
        else:
            f.write(self.private_key.key.exportKey(pkcs=8,
                protection='PBKDF2WithHMAC-SHA1AndAES256-CBC'))
        f.close()


