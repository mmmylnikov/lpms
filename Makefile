# ifneq (,$(wildcard .env))
# 	$(info Found .env file.)
# 	include .env
# 	export
# endif


style:
	flake8 lpms/

types:
	mypy lpms/

pre-commit-all:
	pre-commit run --all-files

check:
	make style types
