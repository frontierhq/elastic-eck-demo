.DEFAULT_GOAL := install

build:

clean:
	find . -type d -name ".terraform" -exec rm -rf "{}" \+

deploy:
	uv run python scripts/deploy.py

destroy:
	uv run python scripts/destroy.py

install:
ifeq ($(CI),true)
	uv sync --frozen
else
	uv sync
	uv run pre-commit install
endif

test: test.lint test.script

test.lint: test.lint.python test.lint.yaml

test.lint.python:
	uv run ruff check scripts
	uv run ruff format --check --diff scripts

test.lint.yaml:
	uv run yamllint .

test.script:
	uv run python scripts/test.py
