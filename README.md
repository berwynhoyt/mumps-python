# Mumps-python for the MUMPS database

## Overview

Mumps-python is a python language plugin for the MUMPS database. It provides the means to call Lua from within M. Mumps-python complements [YDBPython](https://gitlab.com/YottaDB/Lang/YDBPython) (cf. YDB's [Multi-Language Programmer's Guide](https://docs.yottadb.com/MultiLangProgGuide/pythonprogram.html)) which operates in the other direction, letting Python code access an M database.

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

For the sake of speed, it is also possible to pre-compile python code:

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

**`mpy.eval()`** evaluates `code` as a python expression using Python's built-in function `eval()`. Alternatively, `code` may be the handle of a precompiled chunk of code previously returned by `mpy.compile()`. The optional parameter `output` is an M 'actualname' that receives the result of the function. Return 0 on success and return a string representation of the return value in `.output`, if supplied; otherwise on `stdout`. Return <0 on error and return the `repr(exception)` in `.output`, if supplied; otherwise display the whole traceback on `stderr`.

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

## Testing

To test mumps-python, simply type:

```shell
make test  # not implemented yet
```

To perform a set of speed tests, do:

```shell
make benchmark  # not implemented yet
```

## Technical details

### Thread Safety

This needs work.

### Quirks

Need to add note on CPython vs Pypy.

## Troubleshooting

TBD

