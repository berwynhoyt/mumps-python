#!/usr/bin/env python3

""" Version History of mumps-python:
v0.0.1 First version
"""
__version_info__ = 0,0,1  # Maj,Min,Release
__version__ = '{}.{}.{}'.format(*__version_info__)

from mpy import ffi, lib
import sys

mpy_locals = {}
encoding = 'utf-8'

@ffi.def_extern()
def mpy_version_number(_argc):
    return __version_info__[0] * 10000   +   __version_info__[1] * 100  +   __version_info__[2]

def gtm2bytes(gtm_string_t):
    return ffi.unpack(gtm_string_t.address, gtm_string_t.length)

_transtable = b''.maketrans(b'-.eE', b'0000')
def bytes2num(value):
    """ Convert to integer or float if possible; otherwise return original string """
    if value.isdigit(): return int(value)
    if value.startswith(b'-') and value[1:].isdigit(): return int(value)
    if not value.translate(_transtable).isdigit(): return value
    try:
        return float(value)
    except ValueError:
        pass
    return value

def returner(retval, output=None):
    """ Fill gtm_string_t `output` with a string representation of retval encoded into bytes with `encoding`
        if `output` is None, print retval to stdout instead.
    """
    if retval is None:
        retval = b''
    if output is None:
        sys.stdout.write(f"{retval!r}")
        return 0
    maxlen = output.length
    if not isinstance(retval, (bytes, bytearray)):
        retval = f"{retval}".encode(encoding)[:maxlen]
    output.address = ffi.from_buffer(retval)
    output.length = len(retval)
    return 0

@ffi.def_extern()
def mpy_eval(argc, code, output):
    """ Run Python code in globals() scope and with locals=mpy_locals.
        `code` is cdata pointer to a gtm_string_t* (i.e. pointer to bytes).
            If `code`, when evaluated, returns a python code object, that code object is eval()ed instead.
            This way you can run code that you have previously precompiled into a local variable
        `output` (optional) is a cdata pointer to a gtm_string_t* that receives the output of the function.
        return 0 on success and return a string representation of the return value in .output (if supplied) or on stdout
        return <0 on error and return the exception message in .output, if supplied, otherwise display the whole traceback on stderr
        Example of calling from M:
            do &mpy.eval("3+4-1",.result)
    """
    if argc < 2:
        output = None
    # Note: do not overwrite input variables code and output because they 'own' the strings (in cffi terms), keeping them alive
    _code = gtm2bytes(code)
    retval = eval(_code, globals(), mpy_locals)
    if type(retval) == 'code':
        retval = eval(_code, globals(), mpy_locals)
    return returner(retval, output=output)

@ffi.def_extern()
def mpy_exec(argc, code, output):
    """ Run Python code in globals() scope and with locals=mpy_locals.
        `code` is cdata pointer to a gtm_string_t* (i.e. pointer to bytes).
            if you wish to run a precompiled python code object, see mpy_eval()
        `output` (optional) is a cdata pointer to a gtm_string_t* that receives the output of the function.
        return 0 on success
        return <0 on error and return the exception message in .output, if supplied, otherwise display the whole traceback on stderr
        Example of calling from M:
            do &mpy.exec("print(1)")
    """
    if argc < 2:
        output = None
    # Note: do not overwrite input variables code and output because they 'own' the strings (in cffi terms), keeping them alive
    _code = gtm2bytes(code)
    exec(_code, globals(), mpy_locals)
    output.length = 0
    return 0

@ffi.def_extern()
def mpy_vfunc(argc, funcname, output, args):
    """ Run Python function funcname in globals() scope and with locals=mpy_locals.
        `funcname` is a bytearray (actualy, a cdata pointer to a gtm_string_t pointer) which specifies
          a name within scope that references a function run. Allows dot notation like, "math.abs"
        `output` (optional) is a cdata pointer to a gtm_string_t* that receives the output of the function.
        `args` (optional) is a va_args pointer to a list of gtm_string_t strings which specify arguments to pass.
        return 0 on success and return a string representation of the return value in .output (if supplied) or on stdout
        return <0 on error and return the exception message in .output, if supplied, otherwise display the whole traceback on stderr
        Example of calling from M:
            do &mpy.exec("def f(a,b): return a+b")
            do &mpy.func("f",.result,3,4)
            write result,!  ; shows: 7
    """
    if argc < 2:
        output = None
    # Note: do not overwrite input variables func, output, and args because they 'own' the strings (in cffi terms), keeping them alive
    _funcname = gtm2bytes(funcname)
    _args = (bytes2num(gtm2bytes(lib.next_string(args))) for _i in range(argc-2))
    mpy_locals['__args__'] = _args
    retval = eval(_funcname.decode(encoding) + '(*__args__)', globals(), mpy_locals)
    mpy_locals['__args__'] = None
    return returner(retval, output=output)

@ffi.def_extern()
def mpy_vfunc_raw(argc, funcname, output, args):
    """ Same as mpy_vfunc() except does not try to convert args to numbers
        Example of calling from M:
            do &mpy.exec("def f(a,b): return a+b")
            do &mpy.func("f",.result,3,4)
            write result,!  ; shows: 34
    """
    if argc < 2:
        output = None
    # Note: do not overwrite input variables func, output, and args because they 'own' the strings (in cffi terms), keeping them alive
    _funcname = gtm2bytes(funcname)
    _args = (gtm2bytes(lib.next_string(args)) for _i in range(argc-2))
    mpy_locals['__args__'] = _args
    retval = eval(_funcname.decode(encoding) + '(*__args__)', globals(), mpy_locals)
    mpy_locals['__args__'] = None
    return returner(retval, output=output)
