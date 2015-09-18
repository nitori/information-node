
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

class CryptoStreamEncryption(object):
    def initialize_encryption(self):
        pass

    def save_encrypted_info(self, rsa_public_identity, path):
        """ Save this crypto stream's symmetric key required to decrypt it
            to a file, but asymmetrically encrypted with the given crypto
            identity.
        """

        raise RuntimeError("not implemented by crypto stream class")

    def load_encrypted_aes_info(self, rsa_private_identity, path):
        """ Load this crypto stream's symmetric key required to decrypt it
            from a file, decrypted with the private key info of the given
            identity (since it's stored encrypted itself).
        """
        raise RuntimeError("not implemented by crypto stream class")

    def encrypt(self, data):
        raise RuntimeError("not implemented by crypto stream class")

    def decrypt(self, data):
        raise RuntimeError("not implemented by crypto stream class")

    def seekable(self):
        """ Whether this crypto stream supports seeking. """
        return False

    def seek(self):
        raise RuntimeError("crypto stream not seekable")



