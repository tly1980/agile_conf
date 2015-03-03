SHELL := /bin/bash
.PHONY: build test clean nopyc bump register upload

test:
	#cd test && python test.py
	cd test && nosetests test.py
	#

register: dist
	python setup.py sdist register

clean: nopyc
	rm -rf *.egg-info/
	rm -rf ./cover
	rm -rf ./build
	rm -rf ./dist

nopyc:
	find . -name '*.pyc' -delete

dist:
	./setup.py sdist

upload:
	python setup.py sdist upload

