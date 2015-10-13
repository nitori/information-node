
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

import os
import shutil
import tempfile
import unittest

from informationnode.daemon.encryption.identity import Identity

class CryptoIdentityTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_encrypt_decrypt(self):
        identity = Identity()

        # test basic encryption / decryption
        plain_str = b"abc"
        encrypted_str = identity.encrypt(plain_str)
        self.assertNotEqual(plain_str, encrypted_str)
        decrypted_str = identity.decrypt(encrypted_str)
        self.assertEqual(plain_str, decrypted_str)

        # ensure it behaves non-deterministically due to PKCS padding:
        self.assertNotEqual(identity.encrypt(plain_str),
            identity.encrypt(plain_str))

        # ensure a way too long value doesn't give any other error than
        # a ValueError:
        too_long_value = os.urandom(identity.size())
        got_value_error = False
        try:
            result = identity.encrypt(too_long_value)
        except ValueError:
            got_value_error = True
        self.assertTrue(got_value_error)

        # test that the key pair can be stored and restored from a file:
        

