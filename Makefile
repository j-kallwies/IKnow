all:
	./convertUiFiles

clean:
	git clean -f -X -d
	echo "The following files and folders were not removed:"
	git clean -n -x -d

test:
	py.test tests/

testcoverage:
	py.test --cov-report term-missing --cov iknow tests/
