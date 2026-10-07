.PHONY: build test init start stop smoke audit
build:
	mvn -B -ntp package
test:
	mvn -B -ntp test
init:
	python3 src/scripts/manage.py init
start:
	python3 src/scripts/manage.py start
stop:
	python3 src/scripts/manage.py stop
smoke:
	python3 src/scripts/manage.py smoke
audit:
	python3 tests/audit_repository.py
