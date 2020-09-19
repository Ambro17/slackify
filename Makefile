.PHONY: build run test style docs

tunnel:
	ngrok http 3000

build:
	docker build . -t slackify:$(shell date +%s)

run:
	docker run -it --rm -v $(PWD):/app slackify

style:
	docker run --rm slackify flake8

test:
	docker run --rm slackify pytest

checks: build style test
	@echo "✔ All CI Checks Passed"

docs:
	pdoc3 src/slackify \
	--config 'search_query="inurl:github.com/Ambro17/slackify  site:ambro17.github.io/slackify"' \
	--config 'git_link_template="https://github.com/Ambro17/slackify/blob/{commit}/{path}#L{start_line}-L{end_line}"' \
	--template-dir 'templates' \
	--html -o docs --force && \
	cp -r docs/slackify/* docs && rm -rf docs/slackify	