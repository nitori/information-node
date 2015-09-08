
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

class IdentityPublicKey(object):
    def __init__(self, key):
        self.key = key
        if self.key.has_private():
            self.key = self.key.publickey()
    
    def save_to_file(self, path):
        f = open(path, "wb")
        f.write(self.key.exportKey('PEM'))
        f.close()

class IdentityPrivateKey(object):
    def __init__(self, key):
        self.key = key
        if not self.key.has_private():
            raise ValueError("RSA key has no private key info")

class Identity(object):
    """ A cryptographic RSA identity which can be used for asymmetric
        encryption.
    """
    def __init__(self, from_file=None):
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
            key = RSA.importKey(contents.decode("utf-8", "ignore"))
            self.public_key = IdentityPublicKey(key)
            if key.has_private():
                self.private_key = IdentityPrivateKey(key)
            else:
                self.private_key = None

    def encrypt_with_rsa(self, value):
        """ Encrypt an X-bit value with this identity. The length must match
            exactly X bits. If you want to encrypt longer values, use this to
            encrypt an AES key instead and use AES to encrypt your actual data
            stream.

            Returns the encrypted bytes.
        """
        raise RuntimeError("not implemented yet")

    def decrypt_with_rsa(self, value):
        """ Decrypt an X bit long value with this identity.

            This can only be done if this identity contains the private key
            part (which means it cannot be just instantiated from the pure
            public information).

            Returns the decrypted bytes, or raises a ValueError if decryption
            failed.
        """
        raise RuntimeError("not implemented yet")

    def save_to_file(self, path, passphrase=None):
        if self.private_key == None:
            raise RuntimeError("cannot save a full identity without " +\
                "private key information")
        f = open(path, "wb")
        if passphrase == None:
            f.write(self.private_key.key.exportKey('PEM'))
        else:
            f.write(self.private_key.key.exportKey('PEM',
                passphrase=passphrase))
        f.close()


