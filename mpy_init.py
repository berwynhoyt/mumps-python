from mpy import ffi, lib

from version import __version_info__

@ffi.def_extern()
def mpy_version_number(_argc):
    return __version_info__[0] * 10000   +   __version_info__[1] * 100  +   __version_info__[2]

@ffi.def_extern()
def mpy_vpython(argc, code, outstr, args):
    arg1 = lib.next_string(args);
    arg2 = lib.next_string(args);
    print(f"argc={argc}\ncode={code}\noutstr={outstr}\narg1={arg1}\narg2={arg2}")
    return 7
