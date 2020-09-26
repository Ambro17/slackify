.PHONY: build run test style docs

tunnel:
	ngrok http 3000

build:
	docker build . -t slackify

run:
	docker run -it --rm -v $(PWD):/app slackify

style:
	docker run --rm -v $(PWD):/app slackify pre-commit

test:
	docker run --rm slackify pytest

checks: build style test
	@echo "✔ All CI Checks Passed"

docs:
	cd docs && \
	make html && \
	cd -
