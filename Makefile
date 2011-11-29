PYBIN=python
PYCOV=$(PYBIN) -m coverage

.PHONY: clean test test-cover

clean:
	rm -fr */*.pyc */*,cover .coverage htmlcov

test:
	$(PYBIN) -m unittest discover -s test

test-cover: test
	rm -fr .coverage htmlcov
	for x in test/test_*.py ; \
	do \
		env PYTHONPATH="`pwd`" $(PYCOV) run --omit="test/*" -a $$x || exit 1 ; \
	done
	$(PYCOV) html
