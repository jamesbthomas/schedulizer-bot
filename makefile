test: install
	python3 -m pytest tests

install:
	python3 -m pip install discord pytest pickledb

all: install test

clean: install
	python3 -m pip uninstall discord pytest pickledb
