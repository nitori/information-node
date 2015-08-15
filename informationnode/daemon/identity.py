
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
    def __init__(self, from_file=None):
        if from_file == None:
            # generate a new pair
            rng = Random.new().read
            key = RSA.generate(4096, rng)
            self.public_key = IdentityPublicKey(key)
            self.private_key = IdentityPrivateKey(key)
        else:
            # read from file:
            f = open(from_file, "wb")
            contents = f.read(4096 * 1024)  # no more than 4mb
            f.close()
            key = RSA.importKey(f.read())
            self.public_key = IdentityPublicKey(key)
            if key.has_private():
                self.private_key = IdentityPrivateKey(key)
            else:
                self.private_key = None

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


