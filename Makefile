build:

clean:
	find . -type d -name ".terraform" -exec rm -rf "{}" \+

deploy:
	pipenv run python scripts/deploy.py

destroy:
	pipenv run python scripts/destroy.py

install:
	pipenv install --dev
	pipenv run pre-commit install

install_ci:
	pipenv sync

test: test.lint test.script

test.lint: test.lint.python test.lint.yaml

test.lint.python:
	pipenv run flake8 scripts

test.lint.yaml:
	pipenv run yamllint .

test.script:
	pipenv run python scripts/test.py
