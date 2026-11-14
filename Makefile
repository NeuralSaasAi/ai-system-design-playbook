.PHONY: check cases lint-md test-scripts links

## check: run every offline check (what CI runs, minus the external link check)
check: cases lint-md test-scripts

## cases: case study format, catalog, relative links, banned words, GFM-only syntax
cases:
	python3 scripts/check_case_studies.py

## lint-md: markdown style
lint-md:
	npx --yes markdownlint-cli2 "**/*.md"

## test-scripts: unit tests for the checker and the issue forms
test-scripts:
	uv run --quiet --python 3.12 --with pytest --with pyyaml pytest -q scripts/tests

## links: check every link, including external ones (needs network; brew install lychee)
links:
	lychee --config lychee.toml "./**/*.md"
