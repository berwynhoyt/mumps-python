from mpy import ffi

from version import __version_info__

@ffi.def_extern()
def mpy_version_number(_argc):
    return __version_info__[0] * 10000   +   __version_info__[1] * 100  +   __version_info__[2]
