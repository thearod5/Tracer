type-hint:
	env/bin/mypy src/
test:
	cd src && ../env/bin/python3 tests/runner.py
test-coverage:
	cd src && ../env/bin/python3 tests/runner.py --with-coverage --cover-package=api  --cover-min-percentage=90
	rm src/.coverage
lint:
	env/bin/pylint src/api
format:
	env/bin/black src/**/*.py
checklist: format lint test-coverage