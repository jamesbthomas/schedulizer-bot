test: install
	python3 -m pytest tests

install:
	python3 -m pip install discord pytest pickledb
  python3 -m pip install -U python-dotenv

all: install test

clean: install
	python3 -m pip uninstall discord pytest pickledb dotenv
