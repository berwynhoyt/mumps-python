#!/usr/bin/env python3

""" Version History of mumps-python:
v0.0.1 First version
"""
__version_info__ = 0,0,1  # Maj,Min,Release
__version__ = '{}.{}.{}'.format(*__version_info__)

from mpy import ffi, lib
import sys
import traceback

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
        sys.stdout.flush()
        return 0
    maxlen = output.length
    if not isinstance(retval, (bytes, bytearray)):
        retval = f"{retval}".encode(encoding)[:maxlen]
    output.address = ffi.from_buffer(retval)
    output.length = len(retval)
    return 0

def print_error(text):
    sys.stderr.write(text)
    sys.stderr.flush()

def error_handler(exc, exc_value, tb):
    if tb is None:  # happens if there was an error converting the return value after the call
        print_error(repr(exc_value))
        return
    # fetch arguments
    func_locals = tb.tb_frame.f_locals
    output = func_locals.get('output', None)
    argc = func_locals.get('argc')
    if argc < 2 or output is None:
        traceback.print_exception(exc, exc_value, tb)
        return
    returner(repr(exc_value), output)

compilations = {}  # dict of compilations
compilation_index = 0  # position of next index to compile into

@ffi.def_extern(error=-1, onerror=error_handler)
def mpy_compile(argc, code, name, mode, output, flags):
    """ Compile Python code and return a handle to it for running it later with `eval()` or `exec()`
        This simply calls Python's built-in `compile` function with `dont_inherit=True`.
        Note: dont_inherit=True makes the compilation independent of the calling code's __future__ module settings,
        which is desirable, but potentially makes the result slightly different than straight calls of `eval()` or `exec()`.
        (see documentation on dont_inherit in Python docs: https://docs.python.org/3/library/functions.html?highlight=compile#compile
        `code` is an M string of Python code to compile
        `name` is an M string containing a name used to describe the code in error messages: e.g. '<string>' or a filename
        `mode` is an M string that must be `eval`, `exec` or `single` per Python's documentation on `compile()`
        `output` (optional) is an M 'actualname' that receives the result of the function.
        `flags` (optional) is an M string_number that represents flags to pass to Python's `compile()` (default 0)
        Return 0 on success with output containing a handle in the format ">integer". This may be later passed to `eval()` or `exec()`.
        Return <0 on error and return the exception message in .output, if supplied, otherwise display the whole traceback on stderr
        Example of calling from M:
            do &mpy.compile("print(1)",.handle)
            do &mpy.eval(handle)
    """
    global compilations, compilation_index
    if argc < 4:
        output = None
    # Note: do not overwrite input variables code and output because they 'own' the strings (in cffi terms), keeping them alive
    _code = gtm2bytes(code)
    _name = gtm2bytes(name).decode(encoding)
    _mode = gtm2bytes(mode).decode(encoding)
    _flags = 0 if argc < 5 else int(gtm2bytes(flags))
    compilation = compile(_code, _name, _mode, flags=_flags, dont_inherit=True)
    handle = b'>' + str(compilation_index).encode(encoding)
    compilation_index += 1
    compilations[handle] = compilation
    if output is not None:
        output.length = len(handle)
        output.address = ffi.from_buffer(handle)
    return 0

@ffi.def_extern(error=-1, onerror=error_handler)
def mpy_uncompile(argc, handle):
    """ Uncompile Python code (i.e. free a previously compiled piece of code)
        `handle` is an M string previously returned by `mpy_compile()`
        Return 0. No error or exception can occur.
    """
    global compilations
    compilations.pop(gtm2bytes(handle), None)
    return 0

_code_type = type(compile('','','exec'))
@ffi.def_extern(error=-1, onerror=error_handler)
def mpy_eval(argc, code, output):
    """ Evaluate and return a Python expression in globals() scope and with locals=mpy_locals.
        `code` is an M string of Python code or a handle of pre_compiled code, returned by `mpy_compile()`
        `output` (optional) is an M 'actualname' that receives the result of the function.
        Return 0 on success and return a string representation of the return value in .output (if supplied) or on stdout
        Return <0 on error and return the repr(exception) in .output, if supplied; otherwise display the whole traceback on stderr
        Example of calling from M:
            do &mpy.eval("3+4-1",.result)
    """
    if argc < 2:
        output = None
    # Note: do not overwrite input variables code and output because they 'own' the strings (in cffi terms), keeping them alive
    _code = gtm2bytes(code)
    if _code.startswith(b'>'):
        _code = compilations[_code]
    retval = eval(_code, globals(), mpy_locals)
    return returner(retval, output=output)

@ffi.def_extern(error=-1, onerror=error_handler)
def mpy_exec(argc, code, output):
    """ Execute Python code in globals() scope and with locals=mpy_locals.
        `code` is an M string of Python code or a handle of pre_compiled code, returned by `mpy_compile()`
        `output` (optional) is an M 'actualname' that receives the result of the function.
        Return 0 on success and empty output
        Return <0 on error and return the exception message in .output, if supplied, otherwise display the whole traceback on stderr
        Example of calling from M:
            do &mpy.exec("print(1)")
    """
    if argc < 2:
        output = None
    # Note: do not overwrite input variables code and output because they 'own' the strings (in cffi terms), keeping them alive
    _code = gtm2bytes(code)
    if _code.startswith(b'>'):
        _code = compilations[_code]
    exec(_code, globals(), mpy_locals)
    if output is not None:
        output.length = 0
    return 0

@ffi.def_extern(error=-1, onerror=error_handler)
def mpy_vfunc(argc, funcname, output, args):
    """ Run Python function funcname in globals() scope and with locals=mpy_locals.
        `funcname` is an M string which specifies a name within scope that references a function run.
            It allows dot notation like, "math.abs".
        `output` (optional) is an M 'actualname' that receives the result of the function.
        `args` (optional) is a va_args pointer to a list of gtm_string_t strings which specify arguments to pass.
        Return 0 on success and return a string representation of the return value in .output (if supplied) or on stdout
        Return <0 on error and return the exception message in .output, if supplied, otherwise display the whole traceback on stderr
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

@ffi.def_extern(error=-1, onerror=error_handler)
def mpy_vfunc_raw(argc, funcname, output, args):
    """ Same as mpy_vfunc() except it does not try to convert args to numbers
        Example of calling from M:
            do &mpy.exec("def f(a,b): return a+b")
            do &mpy.funcRaw("f",.result,3,4)
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
