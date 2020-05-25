setup:
	python setup.py develop

test: setup
	pytest

tunnel:
	ngrok http 3000
