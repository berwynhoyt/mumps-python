#!/usr/bin/env python3
""" Builder for mumps-python """

import cffi
ffi = cffi.FFI()

import subprocess
YDB_INCLUDES = subprocess.run(['pkg-config', '--cflags', 'yottadb'], capture_output=True, encoding='utf-8').stdout.strip()[2:]

# This is a pseudo #include file in a format that embedding_api() requires since it can't handle #include
mpy_typedefs = """
    typedef ... va_list;
    typedef struct { unsigned long length; char *address; } gtm_string_t;
    typedef long... gtm_long_t;
    typedef int... gtm_int_t;
    """

# This is mpy.h:
mpy_h = """
    gtm_int_t mpy_version_number(int _argc);
    // implemented varargs per: https://foss.heptapod.net/pypy/cffi/-/blob/branch/default/demo/extern_python_varargs.py
    gtm_int_t mpy_vfunc(int argc, const gtm_string_t *code, gtm_string_t *outstr, va_list *args);
    gtm_int_t mpy_vfunc_raw(int argc, const gtm_string_t *code, gtm_string_t *outstr, va_list *args);
    gtm_int_t mpy_eval(int argc, const gtm_string_t *code, gtm_string_t *outstr);
    gtm_int_t mpy_exec(int argc, const gtm_string_t *code, gtm_string_t *outstr);
    gtm_int_t mpy_compile(int argc, const gtm_string_t *code, const gtm_string_t *name, const gtm_string_t *mode, gtm_string_t *output, const gtm_string_t *flags);
    gtm_int_t mpy_uncompile(int argc, const gtm_string_t *handle);
    """

# These are C functions that this library makes available for Python to call
mpy_c_declarations = r"""
    #include <stdarg.h>
    #include <gtmxc_types.h>
""" + mpy_h + r"""
    gtm_int_t mpy_func(int argc, const gtm_string_t *code, gtm_string_t *outstr, ...) {
        va_list ap;
        va_start(ap, outstr);
        gtm_int_t result = mpy_vfunc(argc, code, outstr, &ap);
        va_end(ap);
        return result;
    }
    gtm_int_t mpy_func_raw(int argc, const gtm_string_t *code, gtm_string_t *outstr, ...) {
        va_list ap;
        va_start(ap, outstr);
        gtm_int_t result = mpy_vfunc_raw(argc, code, outstr, &ap);
        va_end(ap);
        return result;
    }

    static gtm_string_t* next_string(va_list *va) {  return va_arg((*va), gtm_string_t*);  }

    #define GTM_STRING(str) {sizeof(str)-1, str}  /* Initializer gtm_string_t */
    static gtm_int_t test(void) {
        char tmp[100] = "<unchanged>";
        gtm_int_t result;

        {
            gtm_string_t output={11, tmp}, code=GTM_STRING("4+5");
            result = mpy_eval(2, &code, &output);
            printf("eval=%d: output='%.*s' (should be '9')\n", result, (int)output.length, output.address);
        }
        {
            gtm_string_t output={11, tmp}, code=GTM_STRING("def f(a,b):\n return a+b");
            result = mpy_exec(2, &code, &output);
            printf("exec=%d: output='%.*s' (should be '')\n", result, (int)output.length, output.address);
        }
        {
            gtm_string_t output={11, tmp}, code=GTM_STRING("f"), arg1=GTM_STRING("3"), arg2=GTM_STRING("4");
            result = mpy_func(4, &code, &output, &arg1, &arg2);
            printf("func=%d: output='%.*s' (should be '7')\n", result, (int)output.length, output.address);
        }
        {
            gtm_string_t output={11, tmp}, code=GTM_STRING("f"), arg1=GTM_STRING("3"), arg2=GTM_STRING("4");
            result = mpy_func_raw(4, &code, &output, &arg1, &arg2);
            printf("func=%d: output='%.*s' (should be '34')\n", result, (int)output.length, output.address);
        }
        {
            gtm_string_t output={11, tmp}, code=GTM_STRING("2**8"), name=GTM_STRING("<string>"), mode=GTM_STRING("eval"), flags=GTM_STRING("0");
            result = mpy_compile(5, &code, &name, &mode, &output, &flags);
            printf("compile=%d: output='%.*s' (should be '>0')\n", result, (int)output.length, output.address);
        }
        {
            gtm_string_t output={11, tmp}, handle=GTM_STRING(">0");
            result = mpy_eval(2, &handle, &output);
            printf("eval=%d: output='%.*s' (should be '256')\n", result, (int)output.length, output.address);
            result = mpy_uncompile(2, &handle);
            printf("uncompile[output]=%d (should be 0)\n", result);
            result = mpy_uncompile(2, &handle);
        }
        return result;
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
