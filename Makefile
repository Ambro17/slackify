.PHONY: build run test style

tunnel:
	ngrok http 3000

build:
	docker build . -t slackify

run:
	docker run -it --rm -v $(PWD):/app slackify

test:
	docker run -it --rm -v $(PWD):/app slackify pytest

style:
	docker run -it --rm -v $(PWD):/app slackify flake8