SHELL = /bin/sh
VERSION := $(shell cat version.txt)
CVS_TAG := v$(shell sed "s/\./_/g" version.txt)
PRODUCT := $(shell cat product.txt)
PRODUCT_NAME := ${PRODUCT}
MODULE := ${PRODUCT}
CVS_URL := :ext:$(USERNAME)@cvs.sourceforge.net:/cvsroot/collective
PYTHON := $(shell which python)
SCP_SERVER := $(USERNAME)@shell.sourceforge.net:/home/groups/i/in/ingeniweb/htdocs/Products

default:
	echo "Nothing to do by default."
	echo .
	echo "Use 'make test' to check against unit tests."
	echo "Use 'make dist' to make a distribution if you are in the CVS."
	echo .
	echo "This Makefile requires cvs2cl.pl script which can be found at http://www.red-bean.com/cvs2cl/cvs2cl.pl"

test:
	echo "If tests fail, please refer to test/runtests.sh script to check your PYTHON_PATH."
	(cd tests ; ./runtests.sh)

changelogfile:
	echo "Refreshing ChangeLog"
	./cvs2cl.pl

apidoc:
	echo "Refreshing API doc"
	mkdir -p doc
	cd doc && $(PYTHON) ./py2htmldoc.py $(PRODUCT_NAME) ..

commit:apidoc changelogfile www
	cvs update
	cvs commit

www:apidoc changelogfile
	scp CHANGES ChangeLog README* ${SCP_SERVER}/${PRODUCT}/
	scp doc/*html ${SCP_SERVER}/${PRODUCT}/api/ || echo ""
	scp website/* ${SCP_SERVER}/${PRODUCT}/ || echo ""

dist:version.txt
	echo .
	echo ${VERSION}
	echo ${CVS_TAG}
	echo ${PRODUCT}

	# Updating
	./cvs2cl.pl
	mkdir dist || echo ""
	echo "When updating, be careful about the '?' files : they must NOT be part of your distribution."
	echo "If you feel that one '?'-tagged file should be in your distribution, add it to the cvs before running 'make dist'."
	cvs update -dP

	# Tagging and archiving
	cvs tag -c ${CVS_TAG}
	(cd dist ; cvs -d${CVS_URL} export -r${CVS_TAG} ${MODULE})
	cp ChangeLog dist/${MODULE}
	(cd dist ; tar -czvf ${PRODUCT}-${VERSION}.tar.gz ${MODULE})
	(cd dist ; rm -rf ${MODULE})


