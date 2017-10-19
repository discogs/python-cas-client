clean:
	find . -name '*.pyc' | xargs rm -Rif
	find . -name '*egg-info' | xargs rm -Rif
	find . -name __pycache__ | xargs rm -Rif
	rm -Rif dist/
	rm -Rif build/

package:
	python setup.py build sdist
