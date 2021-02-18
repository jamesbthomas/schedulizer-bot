test: install
	python3 -m pytest tests

install:
	python3 -m pip install discord pytest pickledb > /dev/null
	python3 -m pip install -U python-dotenv > /dev/null

all: install test

run: install
	python3 main.py

clean: install
	python3 -m pip uninstall discord pytest pickledb dotenv > /dev/null
