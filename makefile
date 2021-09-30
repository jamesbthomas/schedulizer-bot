mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
project_dir := $(dir $(mkfile_path))

test: install
	python3 -m pytest $(project_dir)tests

install:
	python3 -m pip install discord > /dev/null
	python3 -m pip install pytest > /dev/null
	python3 -m pip install pickledb > /dev/null
	python3 -m pip install -U python-dotenv > /dev/null

all: install test

temp:
	which python3 | xargs echo -ne

run: install
	python3 main.py

debug: install
	python3 main.py level=debug

clean: install
	python3 -m pip uninstall discord pytest pickledb dotenv > /dev/null

service: install test
	id -u schedulizer &> /dev/null || useradd schedulizer -M -s /sbin/nologin -U o

	if [ ! -d /opt/schedulizer/ ]; then mkdir /opt/schedulizer/; fi
	cp $(project_dir)main.py /opt/schedulizer/ --remove-destination
	cp $(project_dir)startup.sh /opt/schedulizer/ --remove-destination
	cp $(project_dir)LICENSE /opt/schedulizer/ --remove-destination
	cp -R $(project_dir)classes /opt/schedulizer/ --remove-destination
	cp -R $(project_dir)databases /opt/schedulizer/ --remove-destination
	cp -R $(project_dir)logs /opt/schedulizer/ --remove-destination
	if [ ! -e /opt/schedulizer/.env ]; then echo "TOKEN=" > /opt/schedulizer/.env; fi

	chown -R schedulizer:schedulizer /opt/schedulizer
	chmod -R 744 /opt/schedulizer/*

	echo "[Unit]" > /etc/systemd/system/multi-user.target.wants/schedulizer.service
	echo "Description=Schedulizer Discord Bot Service" >> /etc/systemd/system/multi-user.target.wants/schedulizer.service
	echo "After=NetworkManager.service" >> /etc/systemd/system/multi-user.target.wants/schedulizer.service
	echo "" >> /etc/systemd/system/multi-user.target.wants/schedulizer.service
	echo "[Service]" >> /etc/systemd/system/multi-user.target.wants/schedulizer.service
	echo "ExecStart=/bin/sudo -u schedulizer /opt/schedulizer/startup.sh" >> /etc/systemd/system/multi-user.target.wants/schedulizer.service
	echo "ExecStop=/bin/pkill -u schedulizer main.py" >> /etc/systemd/system/multi-user.target.wants/schedulizer.service
	echo "" >> /etc/systemd/system/multi-user.target.wants/schedulizer.service
	echo "[Install]" >> /etc/systemd/system/multi-user.target.wants/schedulizer.service
	echo "WantedBy=multi-user.target" >> /etc/systemd/system/multi-user.target.wants/schedulizer.service







