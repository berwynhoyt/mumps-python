#!/usr/bin/env python3

import cffi
ffi = cffi.FFI()

import subprocess
YDB_INCLUDES = subprocess.run(['pkg-config', '--cflags', 'yottadb'], capture_output=True, encoding='utf-8').stdout.strip()[2:]

# This is a pseudo #include file in a format that embedding_api() requires since it can't handle #include
mpy_typedefs = """
    typedef ... va_list;
    typedef ... gtm_string_t;
    typedef long... gtm_long_t;
    typedef int... gtm_int_t;
    """

# This is mpy.h:
mpy_h = """
    gtm_int_t mpy_version_number(int _argc);
    // implemented varargs per: https://foss.heptapod.net/pypy/cffi/-/blob/branch/default/demo/extern_python_varargs.py
    gtm_int_t mpy_vpython(int argc, const gtm_string_t *code, gtm_string_t *outstr, va_list *args);
    gtm_long_t mpy_open(int argc, gtm_string_t *outstr, gtm_int_t flags);
    gtm_int_t mpy_close(int argc, long lua_handle);
    """

# These are C functions that this library makes available for Python to call
mpy_c_declarations = """
    #include <stdarg.h>
    #include <gtmxc_types.h>

    static gtm_int_t mpy_vpython(int argc, const gtm_string_t *code, gtm_string_t *outstr, va_list *args);

    static gtm_int_t mpy_python(int argc, const gtm_string_t *code, gtm_string_t *outstr, ...) {
        va_list ap;
        va_start(ap, outstr);
        gtm_int_t result = mpy_vpython(argc, code, outstr, &ap);
        va_end(ap);
        return result;
    }

    static gtm_string_t* next_string(va_list *va) { return va_arg((*va), gtm_string_t*); }

    static gtm_int_t test(void) {
        gtm_string_t tmp={3, "tmp"}, code={8, "print(1)"}, arg1={4, "arg1"}, arg2={4, "arg2"};
        return mpy_python(3, &code, &tmp, &arg1, &arg2);
    }
"""

# prototypes of the C functions that this library makes available for Python to call
ffi.cdef(mpy_typedefs + """
    gtm_string_t* next_string(va_list *);
    static gtm_int_t test(void);
""")

# This file defines the Python functions that are called by the matching C wrapper prototype defined above
with open('mpy_init.py') as f:
    mpy_py = f.read()

ffi.embedding_api(mpy_h)
ffi.set_source_pkgconfig('mpy', ['yottadb'], mpy_c_declarations)
ffi.embedding_init_code(mpy_py)
ffi.compile(target="mpy.*", verbose=True)
