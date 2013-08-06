# CONFIG
.PHONY: all clean ui test testpep8 testunit testcoverage

# MAKE
all: ui

clean:
	git clean -f -X -d
	echo "The following files and folders were not removed:"
	git clean -n -x -d

ui:
	./convertUiFiles

test: testpep8 testunit

testpep8:
	py.test --pep8

unittest:
	py.test tests/

testcoverage:
	py.test --cov-report term-missing --cov iknow tests/
