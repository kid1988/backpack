
install-py3:
	pip3 install -r ./config/requirements-py3.txt --target packages

install-py2:
	pip install -r ./config/requirements-py2.txt --target packages

install-dev: install-py3
	sudo pip install honcho
