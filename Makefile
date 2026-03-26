.PHONY: clean tree commitizen install-dev setup-dev-env install install-pipx install-release test lint format test-html-cov-report sync fetch-tags changelog bump bump-version-minor bump-version-major bump-version-patch push-tag

FILE=VERSION
VERSION=v$(shell cat $(FILE))

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} \;
	find . -type d -name .hypothesis -prune -exec rm -rf {} \;
	find . -type d -name .pytest_cache -prune -exec rm -rf {} \;
	find . -type d -name .mypy_cache -prune -exec rm -rf {} \;
	find . -type d -name .ruff_cache -prune -exec rm -rf {} \;
	find . -type d -name '*.egg-info' -prune -exec rm -rf {} \;
	find . -type f -name .DS_Store -delete
	rm -rf dist/ build/ htmlcov/ .coverage

tree:
	tree promptvault

commitizen:
	pipx ensurepath
	pipx install commitizen
	pipx upgrade commitizen

requirements-dev.txt: requirements-dev.in
	uv pip compile --upgrade requirements-dev.in -o $@

install-dev: requirements-dev.txt
	uv pip install -r requirements-dev.txt

setup-dev-env: install-dev commitizen
	pre-commit install --hook-type pre-commit --hook-type commit-msg

install:
	uv tool install --editable .

install-pipx:
	pipx install --editable .

install-release:
	uv tool install promptvault-py

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

test-html-cov-report:
	pytest --cov-report html --cov=promptvault

fetch-tags:
	git fetch --tags

changelog: setup-dev-env
	cz changelog --unreleased-version $(VERSION)

bump: fetch-tags setup-dev-env
	cz bump

bump-version-minor: fetch-tags setup-dev-env
	cz bump --increment MINOR

bump-version-major: fetch-tags setup-dev-env
	cz bump --increment MAJOR

bump-version-patch: fetch-tags setup-dev-env
	cz bump --increment PATCH

push-tag: fetch-tags
	git push --follow-tags origin main

sync:
	promptvault-sync
