CMFFormController

    CMFFormController replaces the portal_form form validation mechanism from
    Plone.  It should work just fine in plain CMF as well.

Requires

	CMF 1.3+
	Zope 2.5.1+ (Recommending 2.6.0+)

Quickstart

    For CMF 1.4:
    1) Create an external method, module CMFFormController.Install, function: install
    2) Run it

    If you are using CMF 1.3, you will need to get ahold of CMF 1.4 and copy 
    the files FSMetadata.py and FSPythonScript.py from the 1.4 CMFCore directory
    to the 1.3 CMFCore directory.

Documentation

    See www/docs.stx

    Also take a look at the CMFFormControllerDemo product.
