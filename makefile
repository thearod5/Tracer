type-hint:
	venv/bin/mypy src/
test:
	cd src && ../venv/bin/python3 tests/runner.py
test-coverage:
	cd src && ../venv/bin/python3 tests/runner.py --with-coverage --cover-package=api  --cover-min-percentage=90
	rm src/.coverage
lint:
	venv/bin/pylint src/api
format:
	venv/bin/black src/**/*.py
install:
	python3 -m venv venv
	venv/bin/python3 -m pip install --upgrade pip
	venv/bin/pip3 install -r requirements.txt
	mkdir -p "cache/.test"
	rm -f .env && echo "PATH_TO_ROOT=\"$(CURDIR)\"" >>.env && echo "PATH_TO_DATASETS=\"\"" >>.env

checklist: format lint test-coverage