
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

class CryptoStreamEncryption(object):
    """ Abstract class for a crypto stream to either encrypt or decrypt a
        lengthier stream of data with a stream encryption like AES.

        Please note you should use an instance only either for encryption or
        decryption. If you mix the two uses with one single stream instance,
        you'll get garbage results.

        This stream does NOT ensure data authenticity, but it provides an HMAC
        key that is safely stored by save_encrypted_info which can be used for
        data authenticity computations.
    """
    def __init__(self):
        self.offset = 0
        self.hmac_key = os.urandom(64)  # 256bits, e.g. for HMAC SHA256

    def initialize_encryption(self):
        pass

    def get_hmac_key(self):
        """ A key which can be used with an HMAC to ensure data
            authentication.
        """
        return self.hmac_key

    def save_encrypted_info(self, rsa_public_identity, path):
        """ Save this crypto stream's symmetric key required to decrypt it
            to a file, but asymmetrically encrypted with the given crypto
            identity.
        """

        raise RuntimeError("not implemented by crypto stream class")

    def load_encrypted_info(self, rsa_private_identity, path):
        """ Load this crypto stream's symmetric key required to decrypt it
            from a file, decrypted with the private key info of the given
            identity (since it's stored encrypted itself).
        """
        raise RuntimeError("not implemented by crypto stream class")

    def encrypt(self, data):
        self.offset += len(data)
        return None

    def decrypt(self, data):
        self.offset += len(data)
        return None

    def seekable(self):
        """ Whether this crypto stream supports seeking. """
        return False

    def tell(self):
        """ Get the byte offset this stream is into decryption or encryption.
            This offset can be reset/changed with seek.
        """
        return self.offset        

    def seek_step(self):
        """ The amount of bytes that can be seeked in one step. For example,
            if this returns 8 you may only seek to positions 0, 8, 16, ..
        """
        return 1

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
        raise RuntimeError("crypto stream not seekable")



