type_hint:
	env/bin/mypy src/ tests/
test:
	env/bin/nosetests tests
lint:
	env/bin/pylint src/api
checklist:
	lint typehint test
format:
	env/bin/black src/**/*.py