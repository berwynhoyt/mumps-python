# Makefile to build MumpsPython


# ~~~ Variables of interest to user

PREFIX=/usr/local

# Locate YDB install
ydb_dist?=$(shell pkg-config --variable=prefix yottadb --silence-errors)
ifeq ($(ydb_dist),)
  $(error Could not find $$ydb_dist; please install yottadb or set $$ydb_dist to your YDB install')
endif
YDB_INSTALL:=$(ydb_dist)/plugin


# ~~~  Internal variables

YDB_INCLUDES = $(shell pkg-config --cflags yottadb)
PYTHON_INCLUDES = $(shell python3-config --includes)
CFLAGS = -O3 -fPIC -std=c11 -Wall -Werror -Wno-unknown-pragmas  $(YDB_INCLUDES) $(PYTHON_INCLUDES)
LDFLAGS = -lyottadb -L$(ydb_dist) -Wl,-rpath,$(ydb_dist)
CC = gcc

# Core build targets
all: build
build: mpy.so
mpy.so: mpy_init.py build.py
	python3 build.py


# ~~~ Debug

# Print out all variables defined in this makefile
# Warning: these don't work if a variable contains single quotes
vars:
	@echo -e $(foreach v,$(.VARIABLES),$(if $(filter file, $(origin $(v)) ), '\n$(v)=$(value $(v))') )
# Print all vars including those defined by make itself and environment variables
allvars:
	@echo -e $(foreach v,"$(.VARIABLES)", '\n$(v)=$(value $(v))' )


# ~~~ Clean

clean:
	rm -f *.o *.so mpy.c
	rm -rf __pycache__


# ~~~ Test
test: build
	python3 -c "import mpy; mpy.lib.test()"

# ~~~ Install

YDB_DEPLOYMENTS=mpy.so mpy.xc
install: build
	@echo PREFIX=$(PREFIX)
	install -m644 -D $(YDB_DEPLOYMENTS) -t $(YDB_INSTALL)
install-local: PREFIX:=deploy
install-local: YDB_INSTALL:=$(PREFIX)/ydb
install-local: install

remove:
	rm -f $(foreach i,$(YDB_DEPLOYMENTS),$(YDB_INSTALL)/$(i))


#Prevent deletion of targets
.SECONDARY:
#Prevent leaving previous targets lying around and thinking they're up to date if you don't notice a make error
.DELETE_ON_ERROR:

.PHONY: all build test
.PHONY: install install-local
.PHONY: vars allvars
.PHONY: clean
