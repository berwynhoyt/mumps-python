# Python for MUMPS databases

## Overview

Mumps-python is a Python language plugin for MUMPS databases. It provides the means to call Python from within M. Mumps-python complements [YDBPython](https://gitlab.com/YottaDB/Lang/YDBPython) (cf. YDB's [Multi-Language Programmer's Guide](https://docs.yottadb.com/MultiLangProgGuide/pythonprogram.html)) which operates in the other direction, letting Python code access an M database.

Invoking a Python command from M is easy. Here are a few examples:

```lua
$ ydb
YDB>do &mpy.exec("print('Hello World!')")
Hello world!

YDB>do &mpy.eval("3+4")
7
YDB>do &mpy.eval("3+4",.out)
YDB>write out,!
7
```

That last example captures the result into an M variable `out`.

We can also invoke local, global, or module functions:

```lua
YDB>do &mpy.func("max",.out,3,4)  write out
4
YDB>do &mpy.exec("import math")
YDB>do &mpy.func("math.factorial",.out,4)  write out
24
```

String arguments to `mpy.func()` are auto-converted to integers and floats if possible. To avoid this, use `mpy.funcRaw()`.

```lua
YDB>do &mpy.func("type",.out,3)  write out
<class 'int'>
YDB>do &mpy.funcRaw("type",.out,3)  write out
<class 'bytes'>
```

For the sake of speed, it is also possible to pre-compile Python code:

```lua
YDB>do &mpy.compile("sum(range(1000000))","acumulator","eval",.handle)
YDB>do &mpy.eval(handle,.out)
YDB>write out
499999500000
```

### Database access

Now let's access a YDB local variable using YDBPython (which must be installed separately). At the first print statement we'll intentionally create a Python syntax error:

```lua
YDB>do &mpy.exec("import yottadb as ydb")
YDB>set hello="Hello World!"

YDB>do &mpy.eval("ydb.get('hello')".output)
YDB>write output
Hello World!
```

## API

Here is the list of supplied functions, [optional parameters in square brackets]:

- **mpy.eval**(code[,.output])
- **mpy.exec**(code[,.output])
- **mpy.func**(funcname\[,.output]\[,param1]\[,param2]\[,...])
- **mpy.funcRaw**(funcname\[,.output]\[,param1]\[,param2]\[,...])
- **mpy.compile**(code,name,mode\[,output\[,flags=0]])
- **mpy.version**()

**`mpy.eval()`** evaluates `code` as a Python expression using Python's built-in function `eval()`. Alternatively, `code` may be the handle of a precompiled chunk of code previously returned by `mpy.compile()`. The optional parameter `output` is an M 'actualname' that receives the result of the function. Return 0 on success and return a string representation of the return value in `.output`, if supplied; otherwise on `stdout`. Return <0 on error and return the `repr(exception)` in `.output`, if supplied; otherwise display the whole traceback on `stderr`.

**`mpy.exec()`** executes Python `code` Python's built-in function `exec()`. Alternatively, `code` may be the handle of a precompiled chunk of code previously returned by `mpy.compile()`. The optional parameter `output` is an M 'actualname' that receives the result of the function. Return 0 on success (with empty `.output`). Return <0 on error with `repr(exception)` in `.output`, if supplied; otherwise display the whole traceback on `stderr`.

**`mpy.func()`** accepts a string `funcname` that resolves to a local, built-in, or module function (allowing dot notation `math.abs`), and runs it, passing the parameters `args` which are automatically converted, if possible, to integers or floats (in that order of preference). The optional parameter `output` is an M 'actualname' that receives the result of the function. Return the same as `eval()`. Parameter `args` are currently limited to 8, but this may easily be increased in `mpy.xc`.

**`mpy.funcRaw()`** works the same as `mpyfunc()` except does not auto-convert `args` to integers and floats.

**`mpy.compile()`** Compile Python code and return a handle to it for running it later with `eval()` or `exec()`. This simply calls Python's built-in [`compile`](https://docs.python.org/3/library/functions.html?highlight=compile#compile) function (except passing it `dont_inherit=True` which makes the compilation independent of the calling code's __future__ module settings; this is is desirable, but potentially makes the result slightly different than straight calls of `eval()` or `exec()`.)

* `code` is an M string of Python code to compile.
* `name` is an M string containing a name used to describe the code in error messages: e.g. `"<string>"` or a filename.
* `mode` is an M string that must be `eval`, `exec` or `single` per Python's documentation on [`compile()`](https://docs.python.org/3/library/functions.html?highlight=compile#compile)
* `output` (optional) is an M 'actualname' that receives the result of the function.
* `flags` (optional) is an M number that represents the flags to pass to Python's [`compile()`](https://docs.python.org/3/library/functions.html?highlight=compile#compile) (default=0)

Return 0 on success with output containing a handle represented as a string which may be passed to `eval()` or `exec()`.
Return <0 on error and return the exception message in `.output`, if supplied; otherwise display the whole traceback on `stderr`.

**`mpy.uncompile()`** Uncompile Python code (i.e. free a previously compiled piece of code). The parameter `handle` is an M string previously returned by `mpy_compile()`. Return 0 (no error or exception can occur).

**`mpy.version()`** returns the current mumps-python version number as decimal XXYYZZ where XX=major, YY=minor, ZZ=release

## Versions & Acknowledgements

Mumps-python requires YDB 1.34 or higher and Python 3 or higher. It is tested with CPython. It should theoretically work with Pypy but does not currently have an option to load Pypy.

Mumps-python's author is Berwyn Hoyt. Both were sponsored by, and are copyright © 2022, [University of Antwerp Library](https://www.uantwerpen.be/en/library/). They are provided under the same license as YottaDB: the [GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl-3.0.txt).

## Installation

Prerequisites: linux, gcc, yottadb, python
Install YottaDB per the [Quick Start](https://docs.yottadb.com/MultiLangProgGuide/MultiLangProgGuide.html#quick-start) guide instructions or from [source](https://gitlab.com/YottaDB/DB/YDB).

To install mumps-python itself:

```shell
git clone `<mumps-python repository>`
cd mumps-python
make setup  # install cffi for CPython
make  # run ./build.py
sudo make install       # install mpy.so into the system
```

### Pypy

If you prefer PyPy instead of the default CPython, first install PyPy, which is somewhat complicated:

```shell
# substitute appropriate pypy version number in URL and paths
wget https://downloads.python.org/pypy/pypy3.10-v7.3.12-linux64.tar.bz2
sudo tar -xf pypy3.*.bz2 -C/usr/local/lib
sudo mv /usr/local/lib/pypy3.10* /usr/local/lib/pypy3.10
sudo ln -s /usr/local/lib/pypy3.10/bin/pypy /usr/local/bin/pypy3
sudo ln -s /usr/local/lib/pypy3.10/bin/libpypy3.10-c.so /usr/local/lib/libpypy3-c.so
# help ldd load other necessary pypy library paths
sudo ln -s /usr/local/lib/pypy3.10/lib/libffi.so.6 /usr/local/lib/libffi.so.6
sudo ln -s /usr/local/lib/pypy3.10/lib/libtinfow.so.6 /usr/local/lib/libtinfow.so.6
hash -r

echo /usr/local/lib/pypy3.10/lib | sudo tee /etc/ld.so.conf.d/pypy3.conf
sudo ldconfig
# The above 2 lines are for Ubuntu-like systems. On systems where it doesn't work, you might try:
#  LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib/pypy3.10/lib"
```

Now you can rebuild your mpy.so using PyPy as follows:

```shell
make PYTHON=pypy3 clean build
sudo make install
```

Test whether CPython or PyPy are being used:

```shell
$ ydb
YDB>do &mpy.exec("import platform; print(platform.python_implementation())")
PyPy   ;This shows 'CPython' when mpy is still built against PyPy
```

## Testing

To test mumps-python, simply type:

```shell
make test  # not properly implemented yet
```

To perform a set of speed tests, do:

```shell
make benchmark  # not implemented yet
```

## Technical details

### Thread Safety

This needs work.

## Troubleshooting

TBD

## To do

 - Improve speed of mumps-python and check whether it needs a special version tailored for CPython to get calling speed in CPython
 - Address signal safety
 - Weigh up making it work with multiple python interpreters (like Lua does) -- will this be of value, in view of there being only one GIL?

YDBPython could also benefit significantly from speed improvements similar to the ones implemented for lua-yottadb (cachearrays, etc)
