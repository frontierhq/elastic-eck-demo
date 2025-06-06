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

seed:
	uvx esrally race \
		--track elastic/logs \
		--track-params="start_date:2025-05-01,end_date:2025-05-16" \
		--pipeline benchmark-only \
		--target-hosts https://85.210.80.185:9200 \
		--client-options="basic_auth_user:'elastic',basic_auth_password:'3887S6jB8L1RWaq00EtxxOS7',verify_certs:false" \
		--kill-running-processes

test: test.lint test.script

test.lint: test.lint.python test.lint.yaml

test.lint.python:
	uv run ruff check scripts
	uv run ruff format --check --diff scripts

test.lint.yaml:
	uv run yamllint .

test.script:
	uv run python scripts/test.py
