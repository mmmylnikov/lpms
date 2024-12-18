ifneq (,$(wildcard .env))
  $(info Found .env file.)
  include .env
  export
endif

# CORE

style:
	flake8 lpms/

types:
	mypy lpms/

pre-commit-all:
	pre-commit run --all-files

check:
	make style types

# TESTS

pytest:
	pytest lpms/

test:
	make style pytest
