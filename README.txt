CMFFormController

    CMFFormController replaces the portal_form form validation
    mechanism from Plone.  It should work just fine in plain CMF as
    well.

Requires

    CMF 1.3+
    Zope 2.5.1+ (Recommending 2.6.0+)

Quickstart

    For CMF 1.4:
    1) Create an external method, module CMFFormController.Install,
       function: install
    2) Run it

    For CMF 1.3:
    1) Get ahold of CMF 1.4
    2) Copy the files CMFCore/FSMetadata.py and
       CMFCore/FSPythonScript.py from CMF 1.4 to the CMFCore directory
       in your CMF 1.3 install
    3) Replace the line "if self.ZCacheable_isCachingEnabled():" in
       your new FSPythonScript with the line "if 0==1:"
       (Thanks to Laurent Mallet (Ellis))

    Profiling CMFFormController scripts:
    * If you want to use CallProfiler with CMFFormController, you will
      need to download and install the CMFFormControllerPatch product
      from the Collective.
      (Thanks to Andy McKay)

Documentation

    See www/docs.stx
    Also take a look at the CMFFormControllerDemo product.
