# Product-dependant information
PRODUCT_NAME = $(shell cat PRODUCT_NAME)
MAINDIR = $(shell cat PRODUCT_NAME)
ZOPE_USER = zope
ZOPE_GROUP = zope
DISTDIR = dist

# OS-dependant
RM = rm -rf
MKDIR = mkdir -p 
EDITOR = dtemacs
GREP = grep -n '\$$\$$\$$'
CHOWN = chown -R $(ZOPE_USER).$(ZOPE_GROUP)
DEBUG_FILE = $(MAINDIR)/debug.txt
PYTHON=/usr/local/bin/python
FIND= find


# Just-Do-It stuff
default:
	echo "Nothing to do by default"

clean::init
	$(RM) *.pyc *~ *.pyo
	$(FIND) . -name "*~" -exec $(RM) {} \;
	$(RM) $(DISTDIR)/*

init:
	echo "PLEASE USE gmake INSTEAD OF make !!!"
	touch version.txt

export::dist
	$(warning "ENTER THE DESTINATION HOST NAME FOLLOWED BY : AND BY THE (optional) DESTINATION DIRECTORY")
	scp $(DISTDIR)/$(PRODUCT_NAME)-`cat version.txt`.tar.gz $(shell read DEST ; echo $$DEST)

dist::distrib

distrib::clean documentation
	mkdir $(DISTDIR) || echo ""
	cd .. && tar -czf $(MAINDIR)/$(DISTDIR)/$(PRODUCT_NAME)-`cat $(MAINDIR)/version.txt`.tar.gz $(MAINDIR) --exclude $(MAINDIR)/$(DISTDIR) --exclude CVS*

zip::distrib
	mkdir $(DISTDIR) || echo ""
	cd .. && zip -rT9v $(MAINDIR)/$(DISTDIR)/$(PRODUCT_NAME)-`cat $(MAINDIR)/version.txt`.zip $(MAINDIR) -x $(MAINDIR)/$(DISTDIR)

edit:
	$(EDITOR) *py

check:
	$(GREP) *py

install::clean
	cd .. && $(CHOWN) $(MAINDIR)
	rm $(DEBUG_FILE) || echo ""

documentation:
	$(MKDIR) doc
	#cd doc && $(PYTHON) ../../Ingeniweb/py2htmldoc.py $(PRODUCT_NAME) ..

help:
	echo ${PRODUCT_NAME}
	$(shell echo *py)
	echo $(ERR)
	echo ${PRODUCT_NAME}
	$(MAINDIR)
