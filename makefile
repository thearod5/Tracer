type-hint:
	env/bin/mypy src/
test:
	env/bin/nosetests tests
lint:
	env/bin/pylint src/api
format:
	env/bin/black src/**/*.py
checklist:
	format lint typehint test