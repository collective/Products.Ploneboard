Description

  Let Plone users create their own bibliography lists.

  Add-on to the CMFBibliographyAT product written by Raphael Ritz.

What It Does

  * Installs the 'Bibliography List' content type.

Requirements

  * Plone 2.x / CMF 1.4.4 / Archetypes 1.3 (cvs release-1_3-branch, beta2 is not enough)
  
  * CMFBibliographyAT (available from the collective's cvs, "http://cvs.sourceforge.net/viewcvs.py/collective/":http://cvs.sourceforge.net/viewcvs.py/collective/)


Installation

  * Recommanded: Copy ATBiblioList into your Products directory and install it with the 'QuickInstaller' Tool.

  * Or: create an external method at the root of your cmf portal and run it by clicking its 'test' tab.

    - Id           : InstallATBiblioList

    - Title        : Install ATBiblioList (optional)

    - Module Name  : InstallATBiblioList.Install

    - Function Name: install

Contact

  David Convent - david.convent(at)naturalsciences(dot)be

  Louis Wannijn - louis.wannijn(at)naturalsciences(dot)be

To Do

  * Batch view for references widget

  * keep trace of the searches to apply them later on

  * lists should be sortable

  * select all in ref widget

  * default view if no format yet defined (done 040616)

  * complete translation (i18n) support (done)
