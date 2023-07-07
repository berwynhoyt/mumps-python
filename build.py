#!/usr/bin/env python3

import cffi
ffi = cffi.FFI()

import subprocess
YDB_INCLUDES = subprocess.run(['pkg-config', '--cflags', 'yottadb'], capture_output=True, encoding='utf-8').stdout.strip()[2:]

# This is a pseudo #include file in a format that embedding_api() requires since it can't handle #include
mpy_typedefs = """
    typedef ... gtm_string_t;
    typedef long... gtm_long_t;
    typedef int... gtm_int_t;
    """

# This is the real #include
mpy_include = """
    #include <gtmxc_types.h>
    """

# This is mpy.h:
mpy_h = """
    gtm_int_t mpy_version_number(int _argc);
// see calling varargs funcs at: https://foss.heptapod.net/pypy/cffi/-/blob/branch/default/demo/extern_python_varargs.py
//    gtm_int_t mpy(int argc, const gtm_string_t *code, gtm_string_t *outstr, gtm_long_t luaState_handle, ...);
    gtm_long_t mpy_open(int argc, gtm_string_t *outstr, gtm_int_t flags);
    gtm_int_t mpy_close(int argc, long lua_handle);
    """

# These are C functions that this library makes available for Python to call
mpy_c_declarations = ""

# This file defines the Python functions that are called by the matching C wrapper prototype defined above
with open('mpy_init.py') as f:
    mpy_py = f.read()

ffi.embedding_api(mpy_typedefs + mpy_h)
ffi.set_source_pkgconfig('mpy', ['yottadb'], mpy_include + mpy_c_declarations)
ffi.embedding_init_code(mpy_py)
ffi.compile(target="mpy.*", verbose=True)
