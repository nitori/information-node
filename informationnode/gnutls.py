
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

import ctypes
import os
import platform

def dll_import_path():
    if platform.system().lower() == "windows":
        # go up from informationnode/gnutls.py to main folder:
        dir_path = os.path.normpath(os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")))
        
        # see if the dll is there:
        for p in os.listdir(dir_path):
            if p.startswith("libgnutls") and p.endswith(".dll"):
                return os.path.join(dir_path, p)
        raise ImportError("missing GnuTLS library")
    else:
        def check_for_so(path):
            if not os.path.exists(path):
                return None
            for p in os.listdir(path):
                if p.startswith("libgnutls.so"):
                    return os.path.join(path, p)
            return None
        lib64_path = check_for_so("/usr/lib64/")
        if lib64_path != None:
            return lib64_path
        lib_path = check_for_so("/usr/lib/")
        if lib_path != None:
            return lib_path
        return None

_gnutls_dll = None
def load_dll():
    global _gnutls_dll
    path = dll_import_path()

    _gnutls_dll = ctypes.CDLL(path)
    _gnutls_dll.gnutls_global_init.argtypes = tuple()
    _gnutls_dll.restype = ctypes.c_int
    globals()["gnutls_global_init"] = _gnutls_dll.gnutls_global_init

load_dll()

